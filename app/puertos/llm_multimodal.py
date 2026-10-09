"""Extensión del proveedor LLM para imágenes enviadas por el usuario.

El servicio de chat general depende de este contrato, no del SDK de Gemini.
El puerto de texto original conserva su firma para la agenda.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from app.dominio.adjunto import Adjunto


class LLMMultimodal(Protocol):
    @property
    def nombre_modelo(self) -> str: ...

    async def generar(self, instruccion: str, contexto: str) -> str: ...

    async def generar_con_adjuntos(
        self, instruccion: str, contexto: str, adjuntos: Sequence[Adjunto]
    ) -> str: ...
