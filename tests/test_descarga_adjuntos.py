from __future__ import annotations

import asyncio
from types import SimpleNamespace

import httpx
import pytest

from app.bot.descarga_adjuntos import (
    _detectar_mime,
    _host_confiable,
    descargar_imagenes,
)
from app.dominio.adjunto import AdjuntoNoSoportadoError

CONFIG = SimpleNamespace(
    azure_tenant_id="tenant-prueba",
    teams_bot_id="bot-prueba",
    teams_bot_password="secreto-prueba",
)

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 20
URL_TEAMS = "https://smba.trafficmanager.net/amer/x/v3/attachments/1/views/original"


def _ejecutar(attachments, manejador):
    async def escenario():
        transporte = httpx.MockTransport(manejador)
        async with httpx.AsyncClient(transport=transporte) as cliente:
            return await descargar_imagenes(attachments, CONFIG, cliente)

    return asyncio.run(escenario())


def test_descarga_la_imagen_con_el_token_del_bot() -> None:
    peticiones: list[httpx.Request] = []

    def manejador(peticion: httpx.Request) -> httpx.Response:
        peticiones.append(peticion)
        if peticion.url.host == "login.microsoftonline.com":
            return httpx.Response(200, json={"access_token": "TOKEN"})
        return httpx.Response(
            200, content=PNG, headers={"content-type": "application/octet-stream"}
        )

    attachments = [
        {"contentType": "image/*", "contentUrl": URL_TEAMS},
        {"contentType": "text/html", "content": "<p>que es esto</p>"},
    ]

    adjuntos = _ejecutar(attachments, manejador)

    assert len(adjuntos) == 1
    assert adjuntos[0].mime == "image/png"
    assert adjuntos[0].nombre == "imagen.png"
    assert adjuntos[0].datos == PNG
    descarga = peticiones[-1]
    assert descarga.headers["authorization"] == "Bearer TOKEN"


def test_no_envia_el_token_a_hosts_desconocidos() -> None:
    peticiones: list[httpx.Request] = []

    def manejador(peticion: httpx.Request) -> httpx.Response:
        peticiones.append(peticion)
        return httpx.Response(200, content=PNG)

    attachments = [
        {"contentType": "image/png", "contentUrl": "https://ejemplo.com/foto.png"}
    ]

    adjuntos = _ejecutar(attachments, manejador)

    assert len(adjuntos) == 1
    assert len(peticiones) == 1
    assert "authorization" not in peticiones[0].headers


def test_sin_imagenes_no_hace_ninguna_peticion() -> None:
    def manejador(peticion: httpx.Request) -> httpx.Response:
        raise AssertionError("no deberia haber peticiones")

    attachments = [{"contentType": "text/html", "content": "<p>hola</p>"}]

    assert _ejecutar(attachments, manejador) == []


def test_rechaza_enlaces_http() -> None:
    def manejador(peticion: httpx.Request) -> httpx.Response:
        raise AssertionError("no deberia haber peticiones")

    attachments = [
        {
            "contentType": "image/*",
            "contentUrl": "http://smba.trafficmanager.net/x",
        }
    ]

    with pytest.raises(AdjuntoNoSoportadoError):
        _ejecutar(attachments, manejador)


def test_falla_con_un_mensaje_claro_si_la_descarga_da_error() -> None:
    def manejador(peticion: httpx.Request) -> httpx.Response:
        if peticion.url.host == "login.microsoftonline.com":
            return httpx.Response(200, json={"access_token": "TOKEN"})
        return httpx.Response(401)

    attachments = [{"contentType": "image/*", "contentUrl": URL_TEAMS}]

    with pytest.raises(AdjuntoNoSoportadoError, match="No pude descargar"):
        _ejecutar(attachments, manejador)


def test_rechaza_lo_que_no_es_una_imagen_reconocible() -> None:
    def manejador(peticion: httpx.Request) -> httpx.Response:
        if peticion.url.host == "login.microsoftonline.com":
            return httpx.Response(200, json={"access_token": "TOKEN"})
        return httpx.Response(200, content=b"<html>no soy una imagen</html>")

    attachments = [{"contentType": "image/*", "contentUrl": URL_TEAMS}]

    with pytest.raises(AdjuntoNoSoportadoError, match="formato"):
        _ejecutar(attachments, manejador)


def test_detecta_los_formatos_por_los_primeros_bytes() -> None:
    assert _detectar_mime(b"\x89PNG\r\n\x1a\n....") == "image/png"
    assert _detectar_mime(b"\xff\xd8\xff\xe0....") == "image/jpeg"
    assert _detectar_mime(b"GIF89a....") == "image/gif"
    assert _detectar_mime(b"RIFF\x00\x00\x00\x00WEBPVP8 ") == "image/webp"
    assert _detectar_mime(b"texto cualquiera") is None


def test_solo_confia_en_dominios_de_teams() -> None:
    assert _host_confiable("smba.trafficmanager.net")
    assert _host_confiable("us-api.asm.skype.com")
    assert not _host_confiable("ejemplo.com")
    assert not _host_confiable("trafficmanager.net.malo.com")
