"""Descarga de adjuntos desde Teams (por ahora, solo imagenes).

Vive en app/bot porque saber como entrega Teams los archivos es asunto
del canal: el nucleo solo recibe objetos Adjunto ya descargados.

Una imagen pegada en el chat llega como un adjunto con contentType
"image/*" y un contentUrl que exige el token del bot (Authorization:
Bearer). Ese token se pide con las credenciales del bot (client credentials).
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any
from urllib.parse import urlparse

import httpx

from app.config import Configuracion
from app.dominio.adjunto import (
    MAX_BYTES_ADJUNTO,
    Adjunto,
    AdjuntoNoSoportadoError,
)

logger = logging.getLogger(__name__)

_AMBITO_BOT = "https://api.botframework.com/.default"

# El token del bot solo se envia a estos dominios, nunca a una URL cualquiera
# que venga dentro de un mensaje.
_HOSTS_CONFIABLES = ("trafficmanager.net", "botframework.com", "skype.com")

_EXTENSIONES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
}

MAX_IMAGENES = 4


def _campo(adjunto: Any, *nombres: str) -> Any:
    """Lee un campo aceptando snake_case, camelCase, objetos o diccionarios."""
    for nombre in nombres:
        valor = getattr(adjunto, nombre, None)
        if valor is None and isinstance(adjunto, dict):
            valor = adjunto.get(nombre)
        if valor is not None:
            return valor
    return None


def _urls_de_imagenes(attachments: Iterable[Any]) -> list[str]:
    urls: list[str] = []
    for adjunto in attachments:
        tipo = _campo(adjunto, "content_type", "contentType") or ""
        url = _campo(adjunto, "content_url", "contentUrl")
        if isinstance(tipo, str) and tipo.startswith("image/") and isinstance(url, str) and url:
            urls.append(url)
    return urls[:MAX_IMAGENES]


def tiene_imagenes(attachments: Iterable[Any]) -> bool:
    """Detecta imágenes en objetos o diccionarios del SDK de Teams."""
    return bool(_urls_de_imagenes(attachments))


def _host_confiable(host: str) -> bool:
    return any(host == d or host.endswith("." + d) for d in _HOSTS_CONFIABLES)


def _detectar_mime(datos: bytes) -> str | None:
    """Reconoce el formato por los primeros bytes. Teams manda 'image/*'
    y los servidores a veces responden octet-stream, asi que no sirven."""
    if datos.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if datos.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if datos.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        return "image/webp"
    return None


async def _token_del_bot(config: Configuracion, cliente: httpx.AsyncClient) -> str:
    tenant = config.azure_tenant_id or "botframework.com"
    try:
        respuesta = await cliente.post(
            f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": config.teams_bot_id,
                "client_secret": config.teams_bot_password,
                "scope": _AMBITO_BOT,
            },
        )
        respuesta.raise_for_status()
        token = respuesta.json()["access_token"]
        if not isinstance(token, str) or not token:
            raise ValueError("token del bot inválido")
        return token
    except (httpx.HTTPError, KeyError, ValueError) as error:
        logger.warning("No se pudo obtener el token del bot: %s", type(error).__name__)
        raise AdjuntoNoSoportadoError("No pude autenticarme para descargar la imagen.") from error


async def _bajar(url: str, token: str | None, cliente: httpx.AsyncClient) -> bytes:
    cabeceras = {"Authorization": f"Bearer {token}"} if token else {}
    datos = bytearray()
    async with cliente.stream("GET", url, headers=cabeceras, follow_redirects=False) as respuesta:
        respuesta.raise_for_status()
        async for trozo in respuesta.aiter_bytes():
            datos.extend(trozo)
            if len(datos) > MAX_BYTES_ADJUNTO:
                limite = MAX_BYTES_ADJUNTO // (1024 * 1024)
                raise AdjuntoNoSoportadoError(f"La imagen pesa más de {limite} MB.")
    return bytes(datos)


async def _descargar(
    urls: list[str],
    config: Configuracion,
    cliente: httpx.AsyncClient,
) -> list[Adjunto]:
    adjuntos: list[Adjunto] = []
    token: str | None = None

    for posicion, url in enumerate(urls):
        partes = urlparse(url)
        if partes.scheme != "https":
            raise AdjuntoNoSoportadoError("No puedo descargar esa imagen: el enlace no es seguro.")

        if not _host_confiable(partes.hostname or ""):
            raise AdjuntoNoSoportadoError(
                "No puedo descargar imágenes desde ese dominio. Envíala directamente en Teams."
            )
        if token is None:
            token = await _token_del_bot(config, cliente)

        try:
            datos = await _bajar(url, token, cliente)
        except httpx.HTTPError as error:
            estado = getattr(getattr(error, "response", None), "status_code", "?")
            logger.warning(
                "Fallo la descarga de la imagen (estado %s, host %s)",
                estado,
                partes.hostname,
            )
            raise AdjuntoNoSoportadoError(
                "No pude descargar la imagen. Intenta enviarla otra vez."
            ) from error

        mime = _detectar_mime(datos)
        if mime is None:
            raise AdjuntoNoSoportadoError(
                "No reconocí el formato de la imagen. Puedo leer PNG, JPG, WEBP y GIF."
            )

        base = "imagen" if posicion == 0 else f"imagen_{posicion + 1}"
        adjuntos.append(Adjunto(f"{base}.{_EXTENSIONES[mime]}", mime, datos))

    return adjuntos


async def descargar_imagenes(
    attachments: Iterable[Any],
    config: Configuracion,
    cliente: httpx.AsyncClient | None = None,
) -> list[Adjunto]:
    """Descarga las imagenes de la actividad y las devuelve como Adjunto.

    Ignora los adjuntos que no son imagen (el HTML del mensaje, por ejemplo).
    Lanza AdjuntoNoSoportadoError con un mensaje apto para el usuario.
    """
    urls = _urls_de_imagenes(attachments)
    if not urls:
        return []

    if cliente is not None:
        return await _descargar(urls, config, cliente)

    async with httpx.AsyncClient(timeout=20) as propio:
        return await _descargar(urls, config, propio)
