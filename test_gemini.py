import asyncio

from app.adaptadores.gemini_provider import GeminiProvider
from app.config import obtener_configuracion


async def main():
    provider = GeminiProvider(obtener_configuracion())

    respuesta = await provider.generar(
        "Responde brevemente en español.",
        "¿Qué es Python?",
    )

    print("Respuesta de Gemini:")
    print(respuesta)


asyncio.run(main())