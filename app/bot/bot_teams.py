"""Canal de Teams: adaptador PRIMARIO sobre el nucleo de Brujula.

CAPA DE BOT DELGADA — regla que no se negocia:
este modulo traduce mensajes de Teams a llamadas al servicio y respuestas
del servicio a tarjetas. NO decide nada del negocio.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from fastapi import FastAPI
from microsoft_teams.api import MessageActivity, MessageActivityInput, TypingActivityInput
from microsoft_teams.apps import ActivityContext, App
from microsoft_teams.apps.http.fastapi_adapter import FastAPIAdapter

from app.bot.tarjeta_agenda import tarjeta_agenda
from app.config import Configuracion
from app.servicios.servicio_agenda import ServicioAgenda

PATRON_AGENDA = re.compile(r"\b(semana|pendientes|qu[eé]\s+tengo|agenda)\b", re.IGNORECASE)
PATRON_AYUDA = re.compile(r"^\s*(hola|ayuda|help|men[uú]|\?)\s*$", re.IGNORECASE)

AYUDA = (
    "**Brújula** — te ubica entre tus pendientes.\n\n"
    "- **`semana`** — qué tienes en los próximos 7 días\n"
    "- **`ayuda`** — este mensaje\n\n"
    "_Cada pendiente trae enlace a su origen. Los que Brújula infirió de una "
    "conversación salen marcados en amarillo con su nivel de confianza._"
)

FUERA_DE_ALCANCE = (
    "Brújula solo responde sobre tus pendientes. Escribe **`semana`** para ver "
    "los de los próximos 7 días, o **`ayuda`** para ver qué sé hacer."
)


async def construir_respuesta_agenda(
    servicio: ServicioAgenda,
    ahora: datetime,
) -> MessageActivityInput:
    """Consulta la agenda y la convierte en el mensaje que ira a Teams.

    Vive FUERA del handler a proposito: todo lo que queda dentro de un
    handler del SDK solo se puede probar con Teams conectado; todo lo
    que sale de el se prueba con un pytest de 20 milisegundos.
    """
    agenda = await servicio.pendientes_de_la_semana(ahora)
    return MessageActivityInput().add_card(tarjeta_agenda(agenda, ahora))


def crear_bot_teams(
    nucleo: FastAPI,
    servicio: ServicioAgenda,
    config: Configuracion,
) -> App:
    """Monta el canal de Teams sobre la app FastAPI del nucleo.

    Recibe el servicio ya construido: este modulo no crea sus propias
    dependencias. Quien las ensambla es el composition root (app/main.py).
    """
    bot = App(
        http_server_adapter=FastAPIAdapter(app=nucleo),
        messaging_endpoint="/api/messages",
        client_id=config.teams_bot_id or None,
        client_secret=config.teams_bot_password or None,
        tenant_id=config.azure_tenant_id or None,
        dangerously_allow_unauthenticated_requests=not config.teams_bot_id,
    )

    @bot.on_message_pattern(PATRON_AGENDA)
    async def responder_agenda(ctx: ActivityContext[MessageActivity]) -> None:
        await ctx.reply(TypingActivityInput())
        await ctx.send(await construir_respuesta_agenda(servicio, datetime.now(UTC)))

    @bot.on_message_pattern(PATRON_AYUDA)
    async def responder_ayuda(ctx: ActivityContext[MessageActivity]) -> None:
        await ctx.send(AYUDA)

    @bot.on_message
    async def fuera_de_alcance(ctx: ActivityContext[MessageActivity]) -> None:
        """El plan dice: 'si preguntan por recetas de cocina, no responde'."""
        await ctx.send(FUERA_DE_ALCANCE)

    return bot
