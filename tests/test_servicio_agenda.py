from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.dominio.errores import FuenteNoDisponibleError
from app.dominio.pendiente import FuentePendiente, Pendiente
from app.servicios.servicio_agenda import ServicioAgenda

AHORA = datetime(2026, 9, 7, 10, 0, 0)


def _p(id_: str, dias: int | None, confianza: float = 1.0) -> Pendiente:
    return Pendiente(
        id=id_,
        titulo=f"Tarea {id_}",
        fuente=FuentePendiente.PLANNER,
        url_origen=f"https://x/{id_}",
        vence=None if dias is None else AHORA + timedelta(days=dias),
        confianza=confianza,
    )


class FuenteFalsa:
    """Doble de prueba: devuelve lo que se le diga. No hereda de
    TaskSource ni lo importa -- el Protocol no lo exige."""

    def __init__(self, nombre: str, pendientes: list[Pendiente]) -> None:
        self._nombre = nombre
        self._pendientes = pendientes

    @property
    def nombre(self) -> str:
        return self._nombre

    async def obtener_pendientes(self, desde: datetime, hasta: datetime) -> list[Pendiente]:
        return self._pendientes


class FuenteRota:
    """Doble que simula un 403 de Graph."""

    def __init__(self, nombre: str, motivo: str = "403 Forbidden") -> None:
        self._nombre = nombre
        self._motivo = motivo

    @property
    def nombre(self) -> str:
        return self._nombre

    async def obtener_pendientes(self, desde: datetime, hasta: datetime) -> list[Pendiente]:
        raise FuenteNoDisponibleError(self._nombre, self._motivo)


# --- Camino feliz -----------------------------------------------------


async def test_unifica_pendientes_de_varias_fuentes() -> None:
    servicio = ServicioAgenda(
        [
            FuenteFalsa("planner", [_p("a", 2)]),
            FuenteFalsa("calendario", [_p("b", 1)]),
        ]
    )
    agenda = await servicio.pendientes_de_la_semana(AHORA)
    assert agenda.total == 2
    assert agenda.esta_completa is True
    assert set(agenda.fuentes_consultadas) == {"planner", "calendario"}


async def test_ordena_por_fecha_y_deja_los_sin_fecha_al_final() -> None:
    servicio = ServicioAgenda(
        [
            FuenteFalsa("f", [_p("tarde", 5), _p("sin_fecha", None), _p("pronto", 1)]),
        ]
    )
    agenda = await servicio.pendientes_de_la_semana(AHORA)
    assert [p.id for p in agenda.pendientes] == ["pronto", "tarde", "sin_fecha"]


# --- La regla no negociable: fallo != vacio ---------------------------


async def test_una_fuente_caida_no_tumba_las_demas() -> None:
    servicio = ServicioAgenda(
        [
            FuenteFalsa("calendario", [_p("a", 1)]),
            FuenteRota("planner"),
        ]
    )
    agenda = await servicio.pendientes_de_la_semana(AHORA)
    assert agenda.total == 1
    assert agenda.fuentes_consultadas == ("calendario",)


async def test_la_fuente_caida_queda_declarada_explicitamente() -> None:
    """REGLA DE OT-01: nunca decir 'no tienes pendientes' cuando la
    verdad es 'no pude preguntar'."""
    servicio = ServicioAgenda([FuenteRota("planner", "403 Forbidden")])
    agenda = await servicio.pendientes_de_la_semana(AHORA)

    assert agenda.total == 0
    assert agenda.esta_completa is False  # <-- lo que impide la mentira
    assert agenda.fuentes_fallidas[0].nombre == "planner"
    assert "403" in agenda.fuentes_fallidas[0].motivo


async def test_un_bug_inesperado_explota_en_vez_de_disfrazarse() -> None:
    """Un KeyError es un bug propio, no una fuente caida.
    Si se tratara igual, cada bug se disfrazaria de fallo de red."""

    class FuenteConBug:
        @property
        def nombre(self) -> str:
            return "buggy"

        async def obtener_pendientes(self, desde: datetime, hasta: datetime) -> list[Pendiente]:
            raise KeyError("campo inexistente")

    servicio = ServicioAgenda([FuenteConBug()])
    with pytest.raises(KeyError):
        await servicio.pendientes_de_la_semana(AHORA)


# --- Casos borde ------------------------------------------------------


async def test_sin_fuentes_devuelve_agenda_vacia_pero_completa() -> None:
    agenda = await ServicioAgenda([]).pendientes_de_la_semana(AHORA)
    assert agenda.total == 0
    assert agenda.esta_completa is True
