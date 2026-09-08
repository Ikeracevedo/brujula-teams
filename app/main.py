"""
Composition root del proyecto.
"""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.dependencias import obtener_servicio_agenda
from app.api.rutas import VERSION, router
from app.bot.bot_teams import crear_bot_teams
from app.config import obtener_configuracion
import logging

logging.basicConfig(level=logging.DEBUG)

def crear_app() -> FastAPI:
    config = obtener_configuracion()
    servicio = obtener_servicio_agenda()

    @contextlib.asynccontextmanager
    async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
        await app.state.bot_teams.initialize()
        yield

    nucleo = FastAPI(
        title="Brujula",
        version=VERSION,
        description=(
            "Unifica pendientes dispersos de Microsoft 365 y los devuelve con enlace a su origen."
        ),
        lifespan=ciclo_de_vida,
    )
    nucleo.include_router(router)
    nucleo.state.bot_teams = crear_bot_teams(nucleo, servicio, config)

    return nucleo


app = crear_app()
