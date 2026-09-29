"""El adaptador de Gemini se prueba sin llamar a Gemini.

Lo que SI se puede verificar sin red: que la aplicacion arranca sin API
key, que el error se normaliza al dominio, y que el modelo sale de la
configuracion. Lo que NO: que Gemini responda bien — eso es una prueba
manual, y esta en la OT.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.adaptadores.gemini_provider import GeminiProvider
from app.config import Configuracion
from app.dominio.errores import LLMNoDisponibleError


def _config(**kw: Any) -> Configuracion:
    return Configuracion(**kw)


def test_se_puede_construir_sin_api_key() -> None:
    """El defecto que rompia la suite entera: construirlo NO debe fallar.

    En la rama original hacia `raise` en __init__, y como `crear_bot_teams`
    lo construia al importar `app.main`, sin GEMINI_API_KEY la aplicacion no
    arrancaba y `pytest` pasaba de 69 tests a cero por error de recoleccion.
    """
    proveedor = GeminiProvider(_config(gemini_api_key=""))
    assert proveedor.esta_configurado is False


def test_sin_api_key_falla_al_usarlo_no_al_crearlo() -> None:
    """Una funcion opcional degrada cuando se usa; no impide arrancar."""
    import asyncio

    proveedor = GeminiProvider(_config(gemini_api_key=""))
    with pytest.raises(LLMNoDisponibleError) as e:
        asyncio.run(proveedor.generar("instruccion", "contexto"))
    assert "GEMINI_API_KEY" in e.value.motivo
    assert e.value.proveedor == "gemini"


def test_el_modelo_sale_de_la_configuracion() -> None:
    """ADR-006: cambiar de modelo cuesta una variable, no un commit."""
    assert GeminiProvider(_config(gemini_modelo="gemini-9.9-pro")).nombre_modelo == "gemini-9.9-pro"


def test_con_api_key_se_reporta_configurado() -> None:
    assert GeminiProvider(_config(gemini_api_key="clave-de-prueba")).esta_configurado is True
