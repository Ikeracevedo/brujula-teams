"""Canal HTTP/REST: adaptador PRIMARIO sobre el nucleo.

Expone un APIRouter, no una app. Quien construye la app y decide que
canales se montan es el composition root
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencias import obtener_servicio_agenda
from app.api.esquemas import AgendaDTO, SaludDTO
from app.config import obtener_configuracion
from app.servicios.servicio_agenda import ServicioAgenda

VERSION = "0.2.0"

router = APIRouter()


@router.get("/health", response_model=SaludDTO, tags=["operacion"])
async def health() -> SaludDTO:
    config = obtener_configuracion()
    return SaludDTO(estado="ok", version=VERSION, entorno=config.brujula_entorno)


@router.get("/api/agenda", response_model=AgendaDTO, tags=["agenda"])
async def obtener_agenda(
    servicio: Annotated[ServicioAgenda, Depends(obtener_servicio_agenda)],
) -> AgendaDTO:
    """Este endpoint y el handler `semana` del bot llaman al MISMO
    ServicioAgenda. Dos canales, cero logica duplicada."""
    agenda = await servicio.pendientes_de_la_semana(datetime.now(UTC))
    return AgendaDTO.desde_dominio(agenda)
