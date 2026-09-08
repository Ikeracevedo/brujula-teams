"""Capa API. La mas externa y la mas delgada del sistema.

Su unico trabajo: traducir HTTP a llamadas del servicio y el resultado
del servicio a JSON. CERO logica de negocio aqui.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI

from app.api.dependencias import obtener_servicio_agenda
from app.api.esquemas import AgendaDTO, SaludDTO
from app.config import obtener_configuracion
from app.servicios.servicio_agenda import ServicioAgenda

VERSION = "0.1.0"

app = FastAPI(
    title="Brujula",
    version=VERSION,
    description=(
        "Unifica pendientes dispersos de Microsoft 365 y los devuelve "
        "con enlace a su origen."
    ),
)


@app.get("/health", response_model=SaludDTO, tags=["operacion"])
async def health() -> SaludDTO:
    """Sonda de vida (liveness). NO toca fuentes externas: si respondiera
    500 porque Graph esta caido, no estaria midiendo lo que dice medir."""
    config = obtener_configuracion()
    return SaludDTO(estado="ok", version=VERSION, entorno=config.brujula_entorno)


@app.get("/api/agenda", response_model=AgendaDTO, tags=["agenda"])
async def obtener_agenda(
    # Annotated[T, Depends(...)] y NO "servicio: T = Depends(...)": la
    # segunda forma pone una llamada a funcion como valor por defecto,
    # que ruff marca (B008) y ademas ata el tipo al valor.
    servicio: Annotated[ServicioAgenda, Depends(obtener_servicio_agenda)],
) -> AgendaDTO:
    """Pendientes de los proximos 7 dias, de todas las fuentes.

    Este endpoint es la costura del sistema: hoy lo consume el
    navegador; en OT-04 lo consumira el bot de Teams; en F4 lo
    consumira el frontend web. Los tres, sin tocar el nucleo.
    """
    agenda = await servicio.pendientes_de_la_semana(datetime.now(UTC))
    return AgendaDTO.desde_dominio(agenda)
