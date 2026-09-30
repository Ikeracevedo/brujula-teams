"""FuentePlannerGraph se prueba sin Graph, sin red y sin tenant."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from app.adaptadores.graph_planner import FuentePlannerGraph
from app.dominio.errores import FuenteNoDisponibleError, FuenteSinPermisoError
from app.dominio.pendiente import FuentePendiente

AHORA = datetime(2026, 9, 29, 10, 0, tzinfo=UTC)
LUEGO = AHORA + timedelta(days=7)
TENANT = "00000000-0000-0000-0000-000000000001"


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _Tarea:
    def __init__(
        self,
        id: str = "p1",
        title: str = "Tarea Planner",
        percent_complete: int = 0,
        due_date_time: str | None = None,
    ) -> None:
        self.id = id
        self.title = title
        self.percent_complete = percent_complete
        self.due_date_time = due_date_time


class _Respuesta:
    def __init__(self, value: list[Any]) -> None:
        self.value = value


class _ErrorGraph(Exception):
    def __init__(self, codigo: int) -> None:
        self.response_status_code = codigo
        super().__init__(f"Graph {codigo}")


def _graph(tareas: list[Any] | None = None, error: Exception | None = None) -> Any:
    class _Tasks:
        async def get(self, **kwargs: Any) -> Any:
            if error:
                raise error
            return _Respuesta(tareas or [])

    class _Planner:
        def __init__(self) -> None:
            self.tasks = _Tasks()

    class _Me:
        def __init__(self) -> None:
            self.planner = _Planner()

    class _Fake:
        def __init__(self) -> None:
            self.me = _Me()

    return _Fake()


# ---------------------------------------------------------------------------
# Camino feliz
# ---------------------------------------------------------------------------


async def test_traduce_una_tarea_a_pendiente() -> None:
    g = _graph([_Tarea(id="p1", title="Revisar PR")])
    [p] = await FuentePlannerGraph(g, TENANT).obtener_pendientes(AHORA, LUEGO)
    assert p.titulo == "Revisar PR"
    assert p.fuente is FuentePendiente.PLANNER
    assert p.id == "plan-p1"
    assert p.confianza == 1.0


async def test_url_incluye_tenant_y_task_id() -> None:
    g = _graph([_Tarea(id="xyz")])
    [p] = await FuentePlannerGraph(g, TENANT).obtener_pendientes(AHORA, LUEGO)
    assert TENANT in p.url_origen
    assert "xyz" in p.url_origen


async def test_sin_tenant_usa_fallback_valido() -> None:
    g = _graph([_Tarea(id="xyz")])
    [p] = await FuentePlannerGraph(g, tenant_id="").obtener_pendientes(AHORA, LUEGO)
    assert p.url_origen.startswith("https://")


async def test_lista_vacia_es_lista_vacia_no_error() -> None:
    """Tenant sin planes -> lista vacia, no FuenteNoDisponibleError."""
    assert await FuentePlannerGraph(_graph([])).obtener_pendientes(AHORA, LUEGO) == []


# ---------------------------------------------------------------------------
# Contrato del puerto: sin fecha siempre entra
# ---------------------------------------------------------------------------


async def test_tarea_sin_fecha_se_devuelve() -> None:
    g = _graph([_Tarea(due_date_time=None)])
    [p] = await FuentePlannerGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert p.vence is None


async def test_tarea_con_fecha_dentro_de_ventana_entra() -> None:
    fecha = (AHORA + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    g = _graph([_Tarea(due_date_time=fecha)])
    [p] = await FuentePlannerGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert p.vence is not None


async def test_tarea_con_fecha_fuera_de_ventana_se_excluye() -> None:
    fecha = (AHORA + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    g = _graph([_Tarea(due_date_time=fecha)])
    assert await FuentePlannerGraph(g).obtener_pendientes(AHORA, LUEGO) == []


# ---------------------------------------------------------------------------
# Completadas se excluyen
# ---------------------------------------------------------------------------


async def test_percent_complete_100_se_excluye() -> None:
    g = _graph([_Tarea(percent_complete=100, title="Terminada")])
    assert await FuentePlannerGraph(g).obtener_pendientes(AHORA, LUEGO) == []


async def test_percent_complete_50_no_se_excluye() -> None:
    g = _graph([_Tarea(percent_complete=50)])
    assert len(await FuentePlannerGraph(g).obtener_pendientes(AHORA, LUEGO)) == 1


# ---------------------------------------------------------------------------
# Casos borde
# ---------------------------------------------------------------------------


async def test_tarea_sin_titulo_se_descarta_sin_romper() -> None:
    g = _graph([_Tarea(id="a", title="Ok"), _Tarea(id="b", title="  ")])
    [p] = await FuentePlannerGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert p.titulo == "Ok"


async def test_la_fecha_sale_aware() -> None:
    fecha = (AHORA + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    g = _graph([_Tarea(due_date_time=fecha)])
    [p] = await FuentePlannerGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert p.vence is not None
    assert p.vence.tzinfo is not None


# ---------------------------------------------------------------------------
# Errores: fallo != vacio
# ---------------------------------------------------------------------------


async def test_un_403_es_falta_de_permiso() -> None:
    with pytest.raises(FuenteSinPermisoError) as exc:
        await FuentePlannerGraph(_graph(error=_ErrorGraph(403))).obtener_pendientes(AHORA, LUEGO)
    assert exc.value.permiso_requerido == "Tasks.Read"
    assert exc.value.nombre_fuente == "planner"


async def test_un_500_no_es_sin_permiso() -> None:
    with pytest.raises(FuenteNoDisponibleError) as exc:
        await FuentePlannerGraph(_graph(error=_ErrorGraph(500))).obtener_pendientes(AHORA, LUEGO)
    assert not isinstance(exc.value, FuenteSinPermisoError)


async def test_error_de_red_se_reporta() -> None:
    with pytest.raises(FuenteNoDisponibleError):
        await FuentePlannerGraph(_graph(error=TimeoutError("sin red"))).obtener_pendientes(
            AHORA, LUEGO
        )
