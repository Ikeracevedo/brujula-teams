"""Adaptador secundario: Microsoft Planner via Graph API.

Endpoint: GET /me/planner/tasks — tareas asignadas al usuario.
Scope delegado: Tasks.Read. El mismo que FuenteToDoGraph; un consentimiento
en el portal cubre los dos adaptadores.

Diferencia clave respecto a FuenteToDoGraph: dueDateTime de plannerTask
llega como ISO 8601 con sufijo Z ("2024-01-15T00:00:00Z"), no como
DateTimeTimeZone. El campo de completado es percentComplete (0-100), no
un enum de estado. El adaptador abstrae esas diferencias; el dominio no
sabe que Planner y To Do existen.

En un tenant sin planes de Planner la respuesta es lista vacia, no un
error. Una lista vacia no es un fallo: es que no hay tareas asignadas.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.dominio.errores import FuenteNoDisponibleError, FuenteSinPermisoError
from app.dominio.pendiente import FuentePendiente, Pendiente

logger = logging.getLogger(__name__)

NOMBRE = "planner"
PERMISO = "Tasks.Read"
_URL_FALLBACK = "https://tasks.office.com/"


def _url_tarea(tenant_id: str, task_id: str) -> str:
    if tenant_id:
        return f"https://tasks.office.com/{tenant_id}/Home/Task/{task_id}"
    return _URL_FALLBACK


class FuentePlannerGraph:
    """Lee /me/planner/tasks para el usuario autenticado."""

    def __init__(self, cliente_graph: Any, tenant_id: str = "") -> None:
        self._graph = cliente_graph
        self._tenant_id = tenant_id

    @property
    def nombre(self) -> str:
        return NOMBRE

    async def obtener_pendientes(self, desde: datetime, hasta: datetime) -> list[Pendiente]:
        try:
            respuesta = await self._graph.me.planner.tasks.get()
        except Exception as e:
            logger.exception("Error al consultar Planner: %s", e)
            raise self._traducir_error(e) from e

        tareas = getattr(respuesta, "value", None) or []
        return [p for p in (self._a_pendiente(t, desde, hasta) for t in tareas) if p is not None]

    @staticmethod
    def _traducir_error(e: Exception) -> FuenteNoDisponibleError:
        codigo = getattr(e, "response_status_code", None)
        if codigo in (401, 403):
            return FuenteSinPermisoError(NOMBRE, PERMISO)
        return FuenteNoDisponibleError(NOMBRE, f"Graph respondio {codigo or type(e).__name__}")

    def _a_pendiente(self, tarea: Any, desde: datetime, hasta: datetime) -> Pendiente | None:
        # percentComplete == 100 significa completada en Planner.
        # Se descarta aqui porque "100% completado" es vocabulario de Planner,
        # no del dominio.
        if (getattr(tarea, "percent_complete", 0) or 0) == 100:
            return None

        identificador = getattr(tarea, "id", None)
        titulo = (getattr(tarea, "title", None) or "").strip()
        if not identificador or not titulo:
            logger.warning(
                "Tarea de Planner descartada por incompleta: id=%r titulo=%r",
                identificador,
                titulo,
            )
            return None

        vence = self._parsear_fecha(getattr(tarea, "due_date_time", None))

        # Tarea con fecha fuera de ventana: se excluye.
        # Tarea SIN fecha: siempre se incluye (contrato del puerto).
        if vence is not None and not (desde <= vence <= hasta):
            return None

        return Pendiente(
            id=f"plan-{identificador}",
            titulo=titulo,
            fuente=FuentePendiente.PLANNER,
            url_origen=_url_tarea(self._tenant_id, identificador),
            vence=vence,
            confianza=1.0,
        )

    @staticmethod
    def _parsear_fecha(valor: Any) -> datetime | None:
        """ISO 8601 con sufijo Z -> datetime aware UTC.

        Planner devuelve "2024-01-15T00:00:00Z", distinto del DateTimeTimeZone
        de To Do. Esa diferencia es exactamente la razon de tener dos adaptadores.
        """
        if not valor:
            return None
        try:
            return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            logger.warning("Fecha de Planner ilegible: %r", valor)
            return None
