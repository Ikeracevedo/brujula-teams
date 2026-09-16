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
from app.composicion import servicio_para_usuario
from app.config import Configuracion
from app.servicios.servicio_agenda import ServicioAgenda

PATRON_AGENDA = re.compile(r"\b(semana|pendientes|qu[eé]\s+tengo|agenda)\b", re.IGNORECASE)
PATRON_AYUDA = re.compile(r"^\s*(hola|ayuda|help|men[uú]|\?)\s*$", re.IGNORECASE)
PATRON_CONECTAR = re.compile(
    r"^\s*(conectar|conectarme|iniciar\s+sesi[oó]n|login)\s*$", re.IGNORECASE
)
PATRON_DESCONECTAR = re.compile(r"^\s*(desconectar|cerrar\s+sesi[oó]n|logout)\s*$", re.IGNORECASE)
PATRON_ESTADO = re.compile(r"^\s*(estado|status)\s*$", re.IGNORECASE)

AYUDA = (
    "**Brújula** — te ubica entre tus pendientes.\n\n"
    "- **`semana`** — qué tienes en los próximos 7 días\n"
    "- **`conectar`** — autoriza a Brújula a leer tu calendario real\n"
    "- **`desconectar`** — revoca esa autorización\n"
    "- **`estado`** — si tus datos son reales o de ejemplo, ahora mismo\n"
    "- **`ayuda`** — este mensaje\n\n"
    "_Cada pendiente trae enlace a su origen. Los que Brújula infirió de una "
    "conversación salen marcados en amarillo con su nivel de confianza._"
)

FUERA_DE_ALCANCE = (
    "Brújula solo responde sobre tus pendientes. Escribe **`semana`** para ver "
    "los de los próximos 7 días, o **`ayuda`** para ver qué sé hacer."
)

NECESITO_PERMISO = (
    "Para mostrarte tus pendientes reales necesito tu autorización. "
    "Te va a aparecer un botón para iniciar sesión."
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
    config: Configuracion,
) -> App:
    """Monta el canal de Teams sobre la app FastAPI del nucleo.

    Ya no recibe un ServicioAgenda del composition root: con datos reales,
    el servicio se construye POR PETICION, con el cliente de Graph del
    usuario que escribe. Un servicio pasado por fuera y compartido entre
    peticiones seria un servicio cacheado con el token de alguien -- la
    fuga de datos que se evito en F3.
    """
    bot = App(
        http_server_adapter=FastAPIAdapter(app=nucleo),
        messaging_endpoint="/api/messages",
        client_id=config.teams_bot_id or None,
        client_secret=config.teams_bot_password or None,
        tenant_id=config.azure_tenant_id or None,
        dangerously_allow_unauthenticated_requests=not config.teams_bot_id,
        default_connection_name=config.teams_oauth_connection,
    )

    @bot.on_message_pattern(PATRON_AGENDA)
    async def responder_agenda(ctx: ActivityContext[MessageActivity]) -> None:
        await ctx.reply(TypingActivityInput())

        if not ctx.is_signed_in:
            # Honestidad antes que conveniencia: no se le sirven datos de
            # ejemplo a alguien que pidio SUS pendientes. Se le explica y
            # se le ofrece el boton.
            await ctx.send(NECESITO_PERMISO)
            await ctx.sign_in()
            return

        # Servicio construido POR PETICION, con el cliente de Graph de
        # ESTE usuario. Nunca cacheado: un servicio cacheado que lleva el
        # token de alguien le serviria sus datos al siguiente que pregunte.
        servicio_usuario = servicio_para_usuario(ctx.user_graph)
        await ctx.send(await construir_respuesta_agenda(servicio_usuario, datetime.now(UTC)))

    @bot.on_message_pattern(PATRON_CONECTAR)
    async def conectar(ctx: ActivityContext[MessageActivity]) -> None:
        if ctx.is_signed_in:
            await ctx.send("Ya tienes tu cuenta conectada.")
            return
        await ctx.sign_in()

    @bot.on_message_pattern(PATRON_DESCONECTAR)
    async def desconectar(ctx: ActivityContext[MessageActivity]) -> None:
        await ctx.sign_out()
        await ctx.send("Listo, desconecté tu cuenta. Ya no tengo acceso a tus datos reales.")

    @bot.on_message_pattern(PATRON_ESTADO)
    async def estado(ctx: ActivityContext[MessageActivity]) -> None:
        # Nunca adivinar si lo que se muestra es real o de ejemplo: se
        # reporta lo que hay, de verdad, ahora mismo.
        if ctx.is_signed_in:
            await ctx.send("✅ Conectada. `semana` te muestra tus pendientes reales.")
        else:
            await ctx.send("⚪ No conectada. Escribe **`conectar`** para ver tus datos reales.")

    @bot.on_message_pattern(PATRON_AYUDA)
    async def responder_ayuda(ctx: ActivityContext[MessageActivity]) -> None:
        await ctx.send(AYUDA)

    @bot.on_message
    async def fuera_de_alcance(ctx: ActivityContext[MessageActivity]) -> None:
        """El plan dice: 'si preguntan por recetas de cocina, no responde'."""
        await ctx.send(FUERA_DE_ALCANCE)

    return bot
