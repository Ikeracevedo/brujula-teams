from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime

import pytest

from app.adaptadores.memoria_en_proceso import MemoriaEnProceso
from app.dominio.adjunto import (
    MAX_BYTES_ADJUNTO,
    MIME_DOCX,
    Adjunto,
    AdjuntoNoSoportadoError,
)
from app.servicios.servicio_conversacion import ServicioConversacion

AHORA = datetime(2026, 9, 29, tzinfo=UTC)


class LLMRegistro:
    """Doble de LLMProvider: registra contexto y adjuntos recibidos."""

    nombre_modelo = "registro"

    def __init__(self) -> None:
        self.llamadas: list[tuple[str, list[Adjunto]]] = []

    async def generar(
        self,
        instruccion: str,
        contexto: str,
        adjuntos: Sequence[Adjunto] = (),
    ) -> str:
        self.llamadas.append((contexto, list(adjuntos)))
        return "ok"


class ExtractorFalso:
    def extraer_texto(self, datos: bytes) -> str:
        return datos.decode("utf-8")


def _servicio(llm: LLMRegistro, memoria: MemoriaEnProceso | None = None):
    return ServicioConversacion(
        llm,
        memoria or MemoriaEnProceso(),
        extractor_docx=ExtractorFalso(),
    )


def test_pdf_e_imagen_van_directo_al_modelo() -> None:
    llm = LLMRegistro()
    pdf = Adjunto("a.pdf", "application/pdf", b"%PDF")
    img = Adjunto("f.png", "image/png", b"\x89PNG")

    asyncio.run(_servicio(llm).responder("c1", "que es esto?", AHORA, [pdf, img]))

    contexto, adjuntos = llm.llamadas[0]
    assert adjuntos == [pdf, img]
    assert contexto == "que es esto?"


def test_docx_se_convierte_en_texto_y_no_va_como_adjunto() -> None:
    llm = LLMRegistro()
    docx = Adjunto("informe.docx", MIME_DOCX, b"hola mundo")

    asyncio.run(_servicio(llm).responder("c1", "resume", AHORA, [docx]))

    contexto, adjuntos = llm.llamadas[0]
    assert adjuntos == []
    assert 'documento "informe.docx"' in contexto
    assert "hola mundo" in contexto
    assert contexto.endswith("resume")


def test_sin_texto_se_usa_una_pregunta_por_defecto() -> None:
    llm = LLMRegistro()
    pdf = Adjunto("a.pdf", "application/pdf", b"%PDF")

    asyncio.run(_servicio(llm).responder("c1", "", AHORA, [pdf]))

    assert "Resume el contenido" in llm.llamadas[0][0]


def test_tipo_no_soportado_falla_sin_llamar_al_modelo() -> None:
    llm = LLMRegistro()
    exe = Adjunto("virus.exe", "application/octet-stream", b"MZ")

    with pytest.raises(AdjuntoNoSoportadoError):
        asyncio.run(_servicio(llm).responder("c1", "abre esto", AHORA, [exe]))

    assert llm.llamadas == []


def test_archivo_demasiado_grande_falla() -> None:
    llm = LLMRegistro()
    grande = Adjunto("g.pdf", "application/pdf", b"0" * (MAX_BYTES_ADJUNTO + 1))

    with pytest.raises(AdjuntoNoSoportadoError):
        asyncio.run(_servicio(llm).responder("c1", "lee", AHORA, [grande]))

    assert llm.llamadas == []


def test_la_memoria_guarda_la_marca_y_no_el_contenido() -> None:
    llm = LLMRegistro()
    memoria = MemoriaEnProceso()
    docx = Adjunto("secreto.docx", MIME_DOCX, b"contenido confidencial")

    async def escenario():
        await _servicio(llm, memoria).responder("c1", "resume", AHORA, [docx])
        return await memoria.turnos("c1", 10)

    turnos = asyncio.run(escenario())

    assert "[Adjuntos: secreto.docx]" in turnos[0].texto
    assert "confidencial" not in turnos[0].texto