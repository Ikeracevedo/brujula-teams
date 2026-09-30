from __future__ import annotations

from datetime import datetime

from app.dominio.conversacion import Turno
from app.puertos.llm_provider import LLMProvider
from app.puertos.memoria_conversacion import MemoriaConversacion

INSTRUCCION_POR_DEFECTO = (
    "Eres Brujula, un asistente academico. "
    "Responde de forma clara, util y breve en espanol. "
    "Puedes responder preguntas academicas y generales. "
    "Si no sabes algo, dilo honestamente. "
    "Si recibes una conversacion previa, usala solo como referencia para "
    "dar continuidad y responde unicamente al mensaje actual."
)

MAX_CARACTERES_POR_TURNO = 2000

_ETIQUETAS = {"usuario": "Usuario", "asistente": "Brujula"}


def armar_contexto(historial: list[Turno], mensaje: str) -> str:
    """Historial + mensaje actual en un solo texto.

    Sin historial devuelve el mensaje tal cual, igual que antes de tener
    memoria. La instruccion sigue viajando aparte, por el mismo motivo
    que documenta el puerto LLMProvider.
    """
    if not historial:
        return mensaje
    previa = "\n".join(f"{_ETIQUETAS[t.rol]}: {t.texto}" for t in historial)
    return (
        f"Conversacion previa:\n{previa}\n\n"
        f"Mensaje actual del usuario:\n{mensaje}"
    )


def _recortar(texto: str) -> str:
    return texto[:MAX_CARACTERES_POR_TURNO]


class ServicioConversacion:
    """Responde mensajes recordando lo hablado en cada conversacion."""

    def __init__(
        self,
        llm: LLMProvider,
        memoria: MemoriaConversacion,
        instruccion: str = INSTRUCCION_POR_DEFECTO,
        max_turnos: int = 10,
    ) -> None:
        self._llm = llm
        self._memoria = memoria
        self._instruccion = instruccion
        self._max_turnos = max_turnos

    async def responder(
        self,
        conversacion_id: str,
        mensaje: str,
        ahora: datetime,
    ) -> str:
        historial = await self._memoria.turnos(conversacion_id, self._max_turnos)

        respuesta = await self._llm.generar(
            self._instruccion,
            armar_contexto(historial, mensaje),
        )

        # Se guarda DESPUES de responder: si el modelo falla, no queda
        # un mensaje del usuario sin respuesta en el historial.
        await self._memoria.agregar(
            conversacion_id,
            [
                Turno("usuario", _recortar(mensaje), ahora),
                Turno("asistente", _recortar(respuesta), ahora),
            ],
        )
        return respuesta

    async def olvidar(self, conversacion_id: str) -> None:
        await self._memoria.olvidar(conversacion_id)