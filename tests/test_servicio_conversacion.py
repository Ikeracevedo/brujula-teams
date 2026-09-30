from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from app.adaptadores.memoria_en_proceso import MemoriaEnProceso
from app.servicios.servicio_conversacion import ServicioConversacion

AHORA = datetime(2026, 9, 29, tzinfo=UTC)


class LLMEco:
    """Doble de LLMProvider: registra el contexto que recibe."""

    nombre_modelo = "eco"

    def __init__(self) -> None:
        self.contextos: list[str] = []

    async def generar(self, instruccion: str, contexto: str) -> str:
        self.contextos.append(contexto)
        return f"respuesta {len(self.contextos)}"


def test_el_segundo_mensaje_incluye_el_primero() -> None:
    llm = LLMEco()
    servicio = ServicioConversacion(llm, MemoriaEnProceso())

    async def escenario() -> None:
        await servicio.responder("c1", "Me llamo Julia", AHORA)
        await servicio.responder("c1", "Como me llamo?", AHORA)

    asyncio.run(escenario())

    assert llm.contextos[0] == "Me llamo Julia"
    assert "Usuario: Me llamo Julia" in llm.contextos[1]
    assert "Brujula: respuesta 1" in llm.contextos[1]
    assert llm.contextos[1].endswith("Como me llamo?")


def test_conversaciones_distintas_no_se_mezclan() -> None:
    llm = LLMEco()
    servicio = ServicioConversacion(llm, MemoriaEnProceso())

    async def escenario() -> None:
        await servicio.responder("c1", "secreto de c1", AHORA)
        await servicio.responder("c2", "hola desde c2", AHORA)

    asyncio.run(escenario())

    assert llm.contextos[1] == "hola desde c2"


def test_olvidar_borra_el_historial() -> None:
    llm = LLMEco()
    servicio = ServicioConversacion(llm, MemoriaEnProceso())

    async def escenario() -> None:
        await servicio.responder("c1", "algo", AHORA)
        await servicio.olvidar("c1")
        await servicio.responder("c1", "de nuevo", AHORA)

    asyncio.run(escenario())

    assert llm.contextos[1] == "de nuevo"


def test_la_ventana_limita_los_turnos_enviados() -> None:
    llm = LLMEco()
    servicio = ServicioConversacion(llm, MemoriaEnProceso(), max_turnos=2)

    async def escenario() -> None:
        for i in range(5):
            await servicio.responder("c1", f"mensaje {i}", AHORA)

    asyncio.run(escenario())

    ultimo = llm.contextos[-1]
    assert "mensaje 3" in ultimo
    assert "mensaje 0" not in ultimo