"""Adaptador secundario: Microsoft To Do via Graph API.

No existe un endpoint plano /me/todo/tasks; hay que recorrer las listas
(/me/todo/lists) y pedir las tareas de cada una. Se usa asyncio.gather con
return_exceptions=True: una lista rota no cancela las demas, mismo patron
que ServicioAgenda sobre sus fuentes.

Scope delegado: Tasks.Read. Mismo que FuentePlannerGraph; un solo
consentimiento en el portal cubre los dos adaptadores.

Diferencia clave respecto a FuenteCalendarioGraph: dueDateTime de todoTask
es un DateTimeTimeZone (campo date_time naive + campo time_zone por separado),
no una cadena ISO con offset. Se normaliza a UTC aqui; el dominio solo ve
datetime aware.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.dominio.errores import FuenteNoDisponibleError, FuenteSinPermisoError
from app.dominio.pendiente import FuentePendiente, Pendiente

logger = logging.getLogger(__name__)

NOMBRE = "to-do"
PERMISO = "Tasks.Read"
_URL_TAREA_BASE = "https://to-do.office.com/tasks/id/{id}/details"
_URL_FALLBACK = "https://to-do.office.com/tasks/"


class FuenteToDoGraph:
    """Lee /me/todo/lists/{id}/tasks. Una lista rota no tumba las demas."""

    def __init__(self, cliente_graph: Any) -> None:
        self._graph = cliente_graph

    @property
    def nombre(self) -> str:
        return NOMBRE

    async def obtener_pendientes(self, desde: datetime, hasta: datetime) -> list[Pendiente]:
        try:
            respuesta_listas = await self._graph.me.todo.lists.get()
        except Exception as e:
            logger.exception("Error al listar listas de To Do: %s", e)
            raise self._traducir_error(e) from e

        listas = getattr(respuesta_listas, "value", None) or []

        resultados = await asyncio.gather(
            *(self._tareas_de_lista(lista.id, desde, hasta) for lista in listas),
            return_exceptions=True,
        )

        pendientes: list[Pendiente] = []
        for lista, resultado in zip(listas, resultados, strict=True):
            if isinstance(resultado, BaseException):
                # Una lista rota se registra pero no cancela las demas.
                logger.warning(
                    "Lista de To Do '%s' no disponible: %s",
                    getattr(lista, "id", "?"),
                    resultado,
                )
            else:
                pendientes.extend(resultado)

        return pendientes

    async def _tareas_de_lista(
        self, list_id: str, desde: datetime, hasta: datetime
    ) -> list[Pendiente]:
        try:
            respuesta = await self._graph.me.todo.lists.by_todo_task_list_id(list_id).tasks.get()
        except Exception as e:
            raise self._traducir_error(e) from e

        tareas = getattr(respuesta, "value", None) or []
        return [p for p in (self._a_pendiente(t, desde, hasta) for t in tareas) if p is not None]

    @staticmethod
    def _traducir_error(e: Exception) -> FuenteNoDisponibleError:
        codigo = getattr(e, "response_status_code", None)
        if codigo in (401, 403):
            return FuenteSinPermisoError(NOMBRE, PERMISO)
        return FuenteNoDisponibleError(NOMBRE, f"Graph respondio {codigo or type(e).__name__}")

    @staticmethod
    def _normalizar_fecha(dtz: Any) -> datetime | None:
        """DateTimeTimeZone de Graph -> datetime aware en UTC.

        MS Graph devuelve hasta 7 digitos de fraccion de segundo; Python
        acepta hasta 6. Se trunca a 26 caracteres antes de parsear.
        Si la zona no es IANA (p.ej. nombre de Windows), se trata como UTC:
        para fechas de vencimiento la imprecision de huso horario es menor
        que perder el pendiente entero.
        """
        if dtz is None:
            return None
        date_str = getattr(dtz, "date_time", None)
        tz_name = (getattr(dtz, "time_zone", None) or "UTC").strip()
        if not date_str:
            return None
        try:
            dt_naive = datetime.fromisoformat(str(date_str)[:26])
        except (ValueError, TypeError):
            return None

        if tz_name.upper() == "UTC":
            return dt_naive.replace(tzinfo=UTC)

        try:
            from zoneinfo import ZoneInfo  # stdlib Python 3.9+

            zona = ZoneInfo(tz_name)
            return dt_naive.replace(tzinfo=zona).astimezone(UTC)
        except Exception:
            logger.warning("Zona desconocida '%s', tratando como UTC", tz_name)
            return dt_naive.replace(tzinfo=UTC)

    def _a_pendiente(self, tarea: Any, desde: datetime, hasta: datetime) -> Pendiente | None:
        # completed se descarta aqui, no en el servicio: "completado" es
        # vocabulario de To Do, no del dominio.
        if (getattr(tarea, "status", "") or "") == "completed":
            return None

        identificador = getattr(tarea, "id", None)
        titulo = (getattr(tarea, "title", None) or "").strip()
        if not identificador or not titulo:
            logger.warning(
                "Tarea de To Do descartada por incompleta: id=%r titulo=%r",
                identificador,
                titulo,
            )
            return None

        vence = self._normalizar_fecha(getattr(tarea, "due_date_time", None))

        # Tarea con fecha fuera de ventana: se excluye.
        # Tarea SIN fecha: siempre se incluye (contrato del puerto).
        if vence is not None and not (desde <= vence <= hasta):
            return None

        # Graph no devuelve webLink en todoTask; se construye el enlace profundo.
        # Pendiente verificar con clic real que abre la tarea en la app.
        url = _URL_TAREA_BASE.format(id=identificador)

        return Pendiente(
            id=f"todo-{identificador}",
            titulo=titulo,
            fuente=FuentePendiente.TODO,
            url_origen=url,
            vence=vence,
            confianza=1.0,
        )
