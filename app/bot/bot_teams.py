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
from app.composicion import (
    servicio_conversacion,
    servicio_para_usuario,
    servicio_pendientes_propios_para_usuario,
)
from app.config import Configuracion
from app.servicios.servicio_agenda import ServicioAgenda
from app.servicios.servicio_conversacion import ServicioConversacion

PATRON_AGENDA = re.compile(r"\b(semana|pendientes|qu[eé]\s+tengo|agenda)\b", re.IGNORECASE)
PATRON_AYUDA = re.compile(r"^\s*(hola|ayuda|help|men[uú]|\?)\s*$", re.IGNORECASE)
PATRON_CONECTAR = re.compile(
    r"^\s*(conectar|conectarme|iniciar\s+sesi[oó]n|login)\s*$", re.IGNORECASE
)
PATRON_DESCONECTAR = re.compile(r"^\s*(desconectar|cerrar\s+sesi[oó]n|logout)\s*$", re.IGNORECASE)
PATRON_ESTADO = re.compile(r"^\s*(estado|status)\s*$", re.IGNORECASE)
PATRON_RECUERDAME = re.compile(r"^\s*rec[uú][eé]rdame\b", re.IGNORECASE)

AYUDA = (
    "**Brújula** — te ubica entre tus pendientes.\n\n"
    "- **`semana`** — qué tienes en los próximos 7 días\n"
    "- **`recuérdame <texto> [el viernes]`** — anota un pendiente propio\n"
    "- **`conectar`** — autoriza a Brújula a leer tu calendario real\n"
    "- **`desconectar`** — revoca esa autorización\n"
    "- **`estado`** — si tus datos son reales o de ejemplo, ahora mismo\n"
    "- **`ayuda`** — este mensaje\n\n"
    "_También puedes preguntarme en lenguaje natural **sobre tus pendientes** "
    "(«¿qué es lo más urgente?», «¿tengo algo el viernes?»). "
    "Fuera de eso no respondo: no soy un asistente de propósito general._\n\n"
    "_Cada pendiente trae enlace a su origen. Los que Brújula infirió de una "
    "conversación salen marcados en amarillo con su nivel de confianza._"
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


async def construir_respuesta_libre(
    conversacion: ServicioConversacion,
    servicio: ServicioAgenda,
    pregunta: str,
    ahora: datetime,
) -> str:
    """Responde una pregunta libre ACOTADA a la agenda del usuario.

    Vive fuera del handler por el mismo motivo que `construir_respuesta_agenda`:
    lo que queda dentro de un handler solo se prueba con Teams conectado.
    """
    agenda = await servicio.pendientes_de_la_semana(ahora)
    respuesta = await conversacion.responder(pregunta, agenda, ahora)
    return respuesta.texto


def _usuario_id(ctx: ActivityContext) -> str:
    """AAD Object ID del usuario. Se prefiere sobre el ID de canal de Teams.

    aad_object_id es el GUID de Entra ID (el que se usa como clave en Mongo).
    Si no esta disponible se usa from_property.id como fallback.
    """
    from_prop = ctx.activity.from_property
    return (getattr(from_prop, "aad_object_id", None) or getattr(from_prop, "id", "") or "").strip()


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

    # El servicio de conversacion SI se puede construir una vez: no lleva
    # token de nadie. El de agenda NO, y por eso se crea por peticion.
    conversacion = servicio_conversacion(config)

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
        servicio_usuario = servicio_para_usuario(ctx.user_graph, _usuario_id(ctx), config)
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

    @bot.on_message_pattern(PATRON_RECUERDAME)
    async def recuerdame(ctx: ActivityContext[MessageActivity]) -> None:
        """Anota un pendiente propio. Ejemplo: 'recuerdame entregar el informe el viernes'."""
        if not ctx.is_signed_in:
            await ctx.send(NECESITO_PERMISO)
            await ctx.sign_in()
            return

        await ctx.reply(TypingActivityInput())

        usuario = _usuario_id(ctx)
        svc = servicio_pendientes_propios_para_usuario(config, usuario)
        try:
            pendiente = await svc.recordar(ctx.activity.text or "", usuario, datetime.now(UTC))
            if pendiente.vence:
                fecha_str = f"vence el {pendiente.vence.strftime('%d/%m/%Y')}"
            else:
                fecha_str = "sin fecha asignada"
            await ctx.send(f"✅ Anotado: «{pendiente.titulo}», {fecha_str}.")
        except ValueError as e:
            await ctx.send(f"No entendí el pendiente: {e}")

    @bot.on_message
    async def pregunta_libre(ctx: ActivityContext[MessageActivity]) -> None:
        """Pregunta en lenguaje natural SOBRE LOS PENDIENTES del usuario.

        El handler no decide el alcance: se lo pregunta a
        `ServicioConversacion`, que solo le entrega al modelo la agenda de
        esta persona. Si la pregunta no va de pendientes, el servicio
        declina — y eso se puede testear sin Teams y sin gastar cuota.
        """
        if not ctx.is_signed_in:
            # Sin sesion no hay agenda, y sin agenda no hay nada sobre lo
            # que responder. No se inventa ni se responde de cultura general.
            await ctx.send(NECESITO_PERMISO)
            await ctx.sign_in()
            return

        await ctx.reply(TypingActivityInput())
        texto = await construir_respuesta_libre(
            conversacion,
            servicio_para_usuario(ctx.user_graph, _usuario_id(ctx), config),
            ctx.activity.text or "",
            datetime.now(UTC),
        )
        await ctx.send(texto)

    return bot
