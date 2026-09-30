"""FuenteToDoGraph se prueba sin Graph, sin red y sin tenant.

Se le pasa un cliente falso con la misma FORMA que el real. La ventaja
de recibir el cliente por constructor: el adaptador no sabe si le dieron
el de Microsoft o uno de mentira.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from app.adaptadores.graph_todo import FuenteToDoGraph
from app.dominio.errores import FuenteNoDisponibleError, FuenteSinPermisoError
from app.dominio.pendiente import FuentePendiente

AHORA = datetime(2026, 9, 29, 10, 0, tzinfo=UTC)
LUEGO = AHORA + timedelta(days=7)


# ---------------------------------------------------------------------------
# Fakes que simulan graph.me.todo.lists.get() y .by_todo_task_list_id().tasks.get()
# ---------------------------------------------------------------------------


class _DTZ:
    """DateTimeTimeZone minimo."""

    def __init__(self, date_time: str | None = None, time_zone: str = "UTC") -> None:
        self.date_time = date_time
        self.time_zone = time_zone


class _Tarea:
    def __init__(
        self,
        id: str = "t1",
        title: str = "Tarea",
        status: str = "notStarted",
        due_date_time: Any = None,
    ) -> None:
        self.id = id
        self.title = title
        self.status = status
        self.due_date_time = due_date_time


class _Lista:
    def __init__(self, id: str = "l1") -> None:
        self.id = id


class _Respuesta:
    def __init__(self, value: list[Any]) -> None:
        self.value = value


class _TasksEndpoint:
    def __init__(self, tareas: list[Any], error: Exception | None = None) -> None:
        self.tasks = self
        self._tareas = tareas
        self._error = error

    async def get(self, **kwargs: Any) -> Any:
        if self._error:
            raise self._error
        return _Respuesta(self._tareas)


class _ListsEndpoint:
    def __init__(
        self,
        listas: list[Any],
        tareas_por_lista: dict[str, list[Any]],
        error_listas: Exception | None = None,
        errores_por_lista: dict[str, Exception] | None = None,
    ) -> None:
        self._listas = listas
        self._tareas = tareas_por_lista
        self._error = error_listas
        self._errores = errores_por_lista or {}

    async def get(self, **kwargs: Any) -> Any:
        if self._error:
            raise self._error
        return _Respuesta(self._listas)

    def by_todo_task_list_id(self, list_id: str) -> _TasksEndpoint:
        return _TasksEndpoint(
            self._tareas.get(list_id, []),
            self._errores.get(list_id),
        )


class _ErrorGraph(Exception):
    def __init__(self, codigo: int) -> None:
        self.response_status_code = codigo
        super().__init__(f"Graph {codigo}")


def _graph(
    listas: list[_Lista] | None = None,
    tareas_por_lista: dict[str, list[Any]] | None = None,
    error_listas: Exception | None = None,
    errores_por_lista: dict[str, Exception] | None = None,
) -> Any:
    """Fabrica un fake de graph con la forma que usa FuenteToDoGraph."""

    class _Me:
        def __init__(self) -> None:
            self.todo = _Todo()

    class _Todo:
        def __init__(self) -> None:
            self.lists = _ListsEndpoint(
                listas or [_Lista()],
                tareas_por_lista or {},
                error_listas,
                errores_por_lista,
            )

    class _Fake:
        def __init__(self) -> None:
            self.me = _Me()

    return _Fake()


# ---------------------------------------------------------------------------
# Camino feliz
# ---------------------------------------------------------------------------


async def test_traduce_una_tarea_a_pendiente() -> None:
    g = _graph(
        listas=[_Lista("l1")],
        tareas_por_lista={"l1": [_Tarea(id="t1", title="Entregar informe")]},
    )
    [p] = await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert p.titulo == "Entregar informe"
    assert p.fuente is FuentePendiente.TODO
    assert p.id == "todo-t1"
    assert p.confianza == 1.0
    assert p.es_inferido is False


async def test_combina_tareas_de_varias_listas() -> None:
    g = _graph(
        listas=[_Lista("l1"), _Lista("l2")],
        tareas_por_lista={
            "l1": [_Tarea(id="a", title="A")],
            "l2": [_Tarea(id="b", title="B")],
        },
    )
    pendientes = await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert {p.id for p in pendientes} == {"todo-a", "todo-b"}


async def test_sin_listas_devuelve_lista_vacia() -> None:
    g = _graph(listas=[])
    assert await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO) == []


# ---------------------------------------------------------------------------
# Contrato del puerto: sin fecha siempre entra
# ---------------------------------------------------------------------------


async def test_tarea_sin_fecha_se_devuelve_igual() -> None:
    """Tarea abierta sin vencimiento: siempre aparece en la agenda."""
    g = _graph(listas=[_Lista()], tareas_por_lista={"l1": [_Tarea(due_date_time=None)]})
    [p] = await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert p.vence is None


async def test_tarea_con_fecha_dentro_de_ventana_entra() -> None:
    fecha_en_ventana = AHORA + timedelta(days=3)
    dtz = _DTZ(date_time=fecha_en_ventana.strftime("%Y-%m-%dT%H:%M:%S.0000000"))
    g = _graph(listas=[_Lista()], tareas_por_lista={"l1": [_Tarea(due_date_time=dtz)]})
    [p] = await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert p.vence is not None


async def test_tarea_con_fecha_fuera_de_ventana_se_excluye() -> None:
    fecha_fuera = AHORA + timedelta(days=30)
    dtz = _DTZ(date_time=fecha_fuera.strftime("%Y-%m-%dT%H:%M:%S.0000000"))
    g = _graph(listas=[_Lista()], tareas_por_lista={"l1": [_Tarea(due_date_time=dtz)]})
    assert await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO) == []


# ---------------------------------------------------------------------------
# Completadas se excluyen
# ---------------------------------------------------------------------------


async def test_tarea_completada_se_excluye() -> None:
    g = _graph(
        listas=[_Lista()],
        tareas_por_lista={"l1": [_Tarea(status="completed", title="Hecha")]},
    )
    assert await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO) == []


# ---------------------------------------------------------------------------
# Casos borde
# ---------------------------------------------------------------------------


async def test_tarea_sin_titulo_se_descarta_sin_romper_la_agenda() -> None:
    tareas = [_Tarea(id="ok", title="Valida"), _Tarea(id="mal", title="   ")]
    g = _graph(listas=[_Lista()], tareas_por_lista={"l1": tareas})
    [p] = await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert p.titulo == "Valida"


async def test_una_lista_rota_no_impide_devolver_las_otras() -> None:
    g = _graph(
        listas=[_Lista("l1"), _Lista("l2")],
        tareas_por_lista={"l1": [_Tarea(id="buena", title="Ok")]},
        errores_por_lista={"l2": RuntimeError("timeout")},
    )
    pendientes = await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert len(pendientes) == 1
    assert pendientes[0].id == "todo-buena"


async def test_la_fecha_sale_aware_en_utc() -> None:
    dtz = _DTZ(date_time="2026-10-03T00:00:00.0000000", time_zone="UTC")
    g = _graph(listas=[_Lista()], tareas_por_lista={"l1": [_Tarea(due_date_time=dtz)]})
    [p] = await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert p.vence is not None
    assert p.vence.tzinfo is not None


# ---------------------------------------------------------------------------
# Errores: fallo != vacio
# ---------------------------------------------------------------------------


async def test_un_403_es_falta_de_permiso() -> None:
    g = _graph(error_listas=_ErrorGraph(403))
    with pytest.raises(FuenteSinPermisoError) as exc:
        await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert exc.value.permiso_requerido == "Tasks.Read"
    assert exc.value.nombre_fuente == "to-do"


async def test_un_401_tambien_es_falta_de_permiso() -> None:
    g = _graph(error_listas=_ErrorGraph(401))
    with pytest.raises(FuenteSinPermisoError):
        await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)


async def test_un_500_es_fuente_caida_no_sin_permiso() -> None:
    g = _graph(error_listas=_ErrorGraph(500))
    with pytest.raises(FuenteNoDisponibleError) as exc:
        await FuenteToDoGraph(g).obtener_pendientes(AHORA, LUEGO)
    assert not isinstance(exc.value, FuenteSinPermisoError)


async def test_error_de_red_se_reporta() -> None:
    with pytest.raises(FuenteNoDisponibleError):
        await FuenteToDoGraph(_graph(error_listas=TimeoutError("sin red"))).obtener_pendientes(
            AHORA, LUEGO
        )
