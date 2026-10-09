"""Chat general sin red: continuidad, aislamiento y envío de imágenes."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

from app.adaptadores.memoria_en_proceso import MemoriaEnProceso
from app.dominio.adjunto import Adjunto
from app.servicios.servicio_chat_general import ServicioChatGeneral

AHORA = datetime(2026, 10, 9, 10, tzinfo=UTC)


class LLMDoble:
    nombre_modelo = "doble"

    def __init__(self) -> None:
        self.contextos: list[str] = []
        self.imagenes: list[Adjunto] = []

    async def generar(self, instruccion: str, contexto: str) -> str:
        self.contextos.append(contexto)
        return f"Respuesta {len(self.contextos)}"

    async def generar_con_adjuntos(
        self, instruccion: str, contexto: str, adjuntos: Sequence[Adjunto]
    ) -> str:
        self.imagenes.extend(adjuntos)
        return await self.generar(instruccion, contexto)


async def test_recuerda_el_turno_anterior_en_la_misma_conversacion() -> None:
    llm = LLMDoble()
    chat = ServicioChatGeneral(llm, MemoriaEnProceso())

    await chat.responder("usuario-a", "chat-1", "Me llamo Julia", AHORA)
    await chat.responder("usuario-a", "chat-1", "¿Cómo me llamo?", AHORA)

    assert "Me llamo Julia" in llm.contextos[1]
    assert "Respuesta 1" in llm.contextos[1]


async def test_la_memoria_separa_usuarios_del_mismo_chat() -> None:
    llm = LLMDoble()
    chat = ServicioChatGeneral(llm, MemoriaEnProceso())

    await chat.responder("usuario-a", "chat-compartido", "dato privado", AHORA)
    await chat.responder("usuario-b", "chat-compartido", "hola", AHORA)

    assert "dato privado" not in llm.contextos[1]


async def test_olvidar_borra_solo_el_historial_de_ese_usuario() -> None:
    llm = LLMDoble()
    chat = ServicioChatGeneral(llm, MemoriaEnProceso())

    await chat.responder("usuario-a", "chat-1", "secreto A", AHORA)
    await chat.responder("usuario-b", "chat-1", "secreto B", AHORA)
    await chat.olvidar("usuario-a", "chat-1")
    await chat.responder("usuario-a", "chat-1", "hola", AHORA)
    await chat.responder("usuario-b", "chat-1", "hola", AHORA)

    assert "secreto A" not in llm.contextos[2]
    assert "secreto B" in llm.contextos[3]


async def test_imagen_viaja_al_modelo_y_solo_su_nombre_a_memoria() -> None:
    llm = LLMDoble()
    memoria = MemoriaEnProceso()
    chat = ServicioChatGeneral(llm, memoria)
    imagen = Adjunto("pizarra.png", "image/png", b"\x89PNG\r\n\x1a\n123")

    await chat.responder("usuario-a", "chat-1", "¿Qué ves?", AHORA, [imagen])

    assert llm.imagenes == [imagen]
    turnos = await memoria.turnos("usuario-a", "chat-1", 10)
    assert "pizarra.png" in turnos[0].texto
    assert "\x89PNG" not in turnos[0].texto
