"""Brujula - OT-02A / spike desechable.

DOS RESPONSABILIDADES, DELIBERADAMENTE SEPARADAS:

  1. PRUEBA DE PLOMERIA (el spike de verdad)
     El handler `eco` devuelve el mensaje en mayusculas. Cero inteligencia.
     Si responde, la cadena completa funciona:
        Teams -> Bot Framework -> POST /api/messages (dev tunnel) -> localhost:3978

  2. DEMO DE PRODUCTO (para mostrar avance)
     El handler `semana` responde "que tengo esta semana" con una Adaptive Card
     construida desde la entidad `Pendiente` (ADR-005), con datos de FIXTURE.

HONESTIDAD DEL DEMO - no negociable:
  Los datos NO vienen de Microsoft Graph. La tarjeta lo dice en su pie y el bot
  lo repite en `estado`. Demostrar el canal y el modelo de datos es un avance
  real; presentarlo como integracion con Graph seria mentir. Un proyecto que
  exagera su avance pierde la unica moneda que tiene ante un evaluador.

TODO ESTE ARBOL SE BORRA al cerrar la OT-02A. El codigo permanente vive en `app/`.
"""

import asyncio
import re

from azure.identity import ManagedIdentityCredential
from microsoft_teams.api import MessageActivity, MessageActivityInput, TypingActivityInput
from microsoft_teams.apps import ActivityContext, App

from config import Config
from fixtures import pendientes_de_la_semana
from tarjetas import tarjeta_semana

config = Config()


def create_token_factory():
    def get_token(scopes, tenant_id=None):
        credential = ManagedIdentityCredential(client_id=config.APP_ID)
        scopes_list = [scopes] if isinstance(scopes, str) else scopes
        return credential.get_token(*scopes_list).token

    return get_token


app = App(
    token=create_token_factory() if config.APP_TYPE == "UserAssignedMsi" else None,
    skip_auth=not config.APP_ID,
)

BIENVENIDA = (
    "**Brujula** - spike OT-02A\n\n"
    "Escribe **`semana`** para ver la demo de 'que tengo esta semana'.\n\n"
    "Escribe **`estado`** para ver que esta probado y que no.\n\n"
    "Cualquier otra cosa la devuelvo en MAYUSCULAS: eso prueba que el mensaje "
    "viajo de Teams a mi codigo y regreso."
)

ESTADO = (
    "**Estado real de la OT-02A**\n\n"
    "- [x] La plantilla del Toolkit soporta **Python** (marcado Preview en la UI)\n"
    "- [x] SDK `microsoft-teams-apps` **2.0.16 (GA)** - el scaffold pinaba una alpha\n"
    "- [x] El SDK corre sobre **FastAPI + uvicorn + Pydantic** -> confirma el ADR-001\n"
    "- [x] Punto de entrada identificado: **POST /api/messages**, puerto 3978\n"
    "- [x] Entidad `Pendiente` (ADR-005) modelada: `fuente`, `confianza`, `url_origen`\n"
    "- [ ] **Microsoft Graph: NO conectado.** Los datos de la demo son de ejemplo.\n"
    "- [ ] LLM (Gemini): NO conectado. Fase 2.\n\n"
    "_Lo que ves demuestra el canal y el modelo de datos, no la integracion con Graph._"
)


@app.on_message_pattern(re.compile(r"^\s*(semana|pendientes|que tengo|qué tengo)", re.I))
async def semana(ctx: ActivityContext[MessageActivity]) -> None:
    """DEMO: la respuesta que Brujula dara cuando Graph este conectado."""
    await ctx.reply(TypingActivityInput())
    tarjeta = tarjeta_semana(pendientes_de_la_semana())
    await ctx.send(MessageActivityInput().add_card(tarjeta))


@app.on_message_pattern(re.compile(r"^\s*(estado|status)", re.I))
async def estado(ctx: ActivityContext[MessageActivity]) -> None:
    """Transparencia: que esta probado y que no."""
    await ctx.send(ESTADO)


@app.on_message_pattern(re.compile(r"^\s*(hola|hi|hello|ayuda|help|\?)", re.I))
async def bienvenida(ctx: ActivityContext[MessageActivity]) -> None:
    await ctx.send(BIENVENIDA)


@app.on_message
async def eco(ctx: ActivityContext[MessageActivity]) -> None:
    """PRUEBA DE PLOMERIA. Cero logica. Si esto responde, el canal funciona."""
    await ctx.reply(TypingActivityInput())
    await ctx.send(f"Recibi: '{ctx.activity.text}' -> {ctx.activity.text.upper()}")


if __name__ == "__main__":
    asyncio.run(app.start())
