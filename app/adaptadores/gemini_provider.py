from __future__ import annotations

import base64
from collections.abc import Sequence

from google import genai

from app.config import Configuracion
from app.dominio.adjunto import Adjunto
from app.puertos.llm_provider import LLMProvider


def _parte(adjunto: Adjunto) -> dict[str, str]:
    """Convierte un Adjunto en una parte de la Interactions API."""
    tipo = "image" if adjunto.mime.startswith("image/") else "document"
    return {
        "type": tipo,
        "data": base64.b64encode(adjunto.datos).decode("utf-8"),
        "mime_type": adjunto.mime,
    }


class GeminiProvider:
    """Implementación de LLMProvider usando la API de Google Gemini."""

    def __init__(self, configuracion: Configuracion) -> None:
        if not configuracion.gemini_api_key:
            raise ValueError("GEMINI_API_KEY no está configurada.")

        self._client = genai.Client(
            api_key=configuracion.gemini_api_key
        )

    @property
    def nombre_modelo(self) -> str:
        return "gemini-3.6-flash"

    async def generar(
        self,
        instruccion: str,
        contexto: str,
        adjuntos: Sequence[Adjunto] = (),
    ) -> str:
        if adjuntos:
            entrada = [
                *(_parte(a) for a in adjuntos),
                {"type": "text", "text": contexto},
            ]
        else:
            entrada = contexto

        response = await self._client.aio.interactions.create(
            model=self.nombre_modelo,
            system_instruction=instruccion,
            input=entrada,
        )

        return response.output_text or ""
