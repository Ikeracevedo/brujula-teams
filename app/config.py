from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    brujula_entorno: str = "local"
    brujula_log_level: str = "INFO"

    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    azure_redirect_uri: str = "http://localhost:8000/auth/callback"

    gemini_api_key: str = ""
    mongodb_uri: str = ""


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve la configuracion, leida del entorno una sola vez.

    lru_cache la convierte en singleton: el .env se lee en la primera
    llamada y se reutiliza despues. En los tests se limpia con
    obtener_configuracion.cache_clear().
    """
    return Configuracion()
