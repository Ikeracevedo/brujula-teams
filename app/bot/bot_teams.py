
"""Canal de Teams: adaptador PRIMARIO sobre el núcleo de Brújula.

CAPA DE BOT DELGADA — regla que no se negocia:
este módulo traduce mensajes de Teams a llamadas al servicio y respuestas
del servicio a tarjetas.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from fastapi import FastAPI
from microsoft_teams.api import (
    MessageActivity,
    MessageActivityInput,
    TypingActivityInput,
)
from microsoft_teams.apps import ActivityContext, App
from microsoft_teams.apps.http.fastapi_adapter import FastAPIAdapter

from app.bot.tarjeta_agenda import tarjeta_agenda
from app.composicion import proveedor_gemini, servicio_para_usuario
from app.config import Configuracion
from app.servicios.servicio_agenda import ServicioAgenda


PATRON_AGENDA = re.compile(
    r"\b(semana|pendientes|qu[eé]\s+tengo|agenda)\b",
    re.IGNORECASE,
)

PATRON_AYUDA = re.compile(
    r"^\s*(hola|ayuda|help|men[uú]|\?)\s*$",
    re.IGNORECASE,
)

PATRON_CONECTAR = re.compile(
    r"^\s*(conectar|conectarme|iniciar\s+sesi[oó]n|login)\s*$",
    re.IGNORECASE,
)

PATRON_DESCONECTAR = re.compile(
    r"^\s*(desconectar|cerrar\s+sesi[oó]n|logout)\s*$",
    re.IGNORECASE,
)

PATRON_ESTADO = re.compile(
    r"^\s*(estado|status)\s*$",
    re.IGNORECASE,
)


AYUDA = (
    "**Brújula** — te ubica entre tus pendientes.\n\n"
    "- **`semana`** — qué tienes en los próximos 7 días\n"
    "- **`conectar`** — autoriza a Brújula a leer tu calendario real\n"
    "- **`desconectar`** — revoca esa autorización\n"
    "- **`estado`** — si tus datos son reales o de ejemplo, ahora mismo\n"
    "- **`ayuda`** — este mensaje\n\n"
    "_También puedes hacer preguntas académicas y generales, "
    "y Brújula las responderá con Gemini._"
)


NECESITO_PERMISO = (
    "Para mostrarte tus pendientes reales necesito tu autorización. "
    "Te va a aparecer un botón para iniciar sesión."
)


async def construir_respuesta_agenda(
    servicio: ServicioAgenda,
    ahora: datetime,
) -> MessageActivityInput:
    """Consulta la agenda y la convierte en el mensaje que irá a Teams."""

    agenda = await servicio.pendientes_de_la_semana(ahora)

    return MessageActivityInput().add_card(
        tarjeta_agenda(agenda, ahora)
    )


def crear_bot_teams(
    nucleo: FastAPI,
    config: Configuracion,
) -> App:
    """Monta el canal de Teams sobre la app FastAPI del núcleo."""

    print("CREANDO BOT DE TEAMS")

    bot = App(
        http_server_adapter=FastAPIAdapter(app=nucleo),
        messaging_endpoint="/api/messages",
        client_id=config.teams_bot_id or None,
        client_secret=config.teams_bot_password or None,
        tenant_id=config.azure_tenant_id or None,
        dangerously_allow_unauthenticated_requests=not config.teams_bot_id,
        default_connection_name=config.teams_oauth_connection,
    )


    gemini = proveedor_gemini(config)

    
    @bot.on_message_pattern(PATRON_AGENDA)
    async def responder_agenda(
        ctx: ActivityContext[MessageActivity],
    ) -> None:

        print(f"Mensaje: {ctx.activity.text}")

        await ctx.reply(TypingActivityInput())

        if not ctx.is_signed_in:
            print("Usuario no autenticado")

            await ctx.send(NECESITO_PERMISO)
            await ctx.sign_in()
            return

        print("Usuario autenticado")

        servicio_usuario = servicio_para_usuario(ctx.user_graph)

        await ctx.send(
            await construir_respuesta_agenda(
                servicio_usuario,
                datetime.now(UTC),
            )
        )

    @bot.on_message_pattern(PATRON_CONECTAR)
    async def conectar(
        ctx: ActivityContext[MessageActivity],
    ) -> None:

        print("HANDLER CONECTAR EJECUTADO")

        if ctx.is_signed_in:
            await ctx.send("Ya tienes tu cuenta conectada.")
            return

        await ctx.sign_in()

    @bot.on_message_pattern(PATRON_DESCONECTAR)
    async def desconectar(
        ctx: ActivityContext[MessageActivity],
    ) -> None:

        print("HANDLER DESCONECTAR EJECUTADO")

        await ctx.sign_out()

        await ctx.send(
            "Listo, desconecté tu cuenta. Ya no tengo acceso a tus datos reales."
        )

    @bot.on_message_pattern(PATRON_ESTADO)
    async def estado(
        ctx: ActivityContext[MessageActivity],
    ) -> None:

        print("HANDLER ESTADO EJECUTADO")

        if ctx.is_signed_in:
            await ctx.send(
                "Conectada. `semana` te muestra tus pendientes reales."
            )
        else:
            await ctx.send(
                "No conectada. Escribe **`conectar`** para ver tus datos reales."
            )

    @bot.on_message_pattern(PATRON_AYUDA)
    async def responder_ayuda(
        ctx: ActivityContext[MessageActivity],
    ) -> None:

        print("HANDLER AYUDA EJECUTADO")
        print(f"Mensaje: {ctx.activity.text}")

        await ctx.send(AYUDA)


    @bot.on_message
    async def responder_con_gemini(
        ctx: ActivityContext[MessageActivity],
    ) -> None:
        """Envía las preguntas generales a Gemini."""

        print("")
        print("=" * 60)
        print("GEMINI HANDLER EJECUTADO")
        print("=" * 60)

        mensaje = ctx.activity.text or ""

        print(f"ENSAJE RECIBIDO: {mensaje}")

        try:
            print("Enviando mensaje a Gemini...")

            respuesta = await gemini.generar(
                instruccion=(
                    "Eres Brújula, un asistente académico. "
                    "Responde de forma clara, útil y breve en español. "
                    "Puedes responder preguntas académicas y generales. "
                    "Si no sabes algo, dilo honestamente."
                ),
                contexto=mensaje,
            )

            print(" GEMINI RESPONDIÓ")
            print(f"RESPUESTA: {respuesta}")

            await ctx.send(respuesta)

            print("RESPUESTA ENVIADA A TEAMS")

        except Exception as error:
            print("")
            print(" ERROR AL USAR GEMINI")
            print(f" {type(error).__name__}: {error}")
            print("")

            await ctx.send(
                "Lo siento, tuve un problema al consultar Gemini."
            )




    return bot

