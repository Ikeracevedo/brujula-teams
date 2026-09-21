from __future__ import annotations

from google import genai

from app.config import Configuracion
from app.puertos.llm_provider import LLMProvider


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

    async def generar(self, instruccion: str, contexto: str) -> str:
        response = await self._client.aio.interactions.create(
            model=self.nombre_modelo,
            system_instruction=instruccion,
            input=contexto,
        )

        return response.output_text or ""