
import os

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
)
from botbuilder.schema import Activity




app = FastAPI(
    title="EduAssist",
    description="Asistente académico inteligente",
    version="1.0.0"
)




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




APP_ID = os.getenv("MicrosoftAppId", "")
APP_PASSWORD = os.getenv("MicrosoftAppPassword", "")
APP_TENANT_ID = os.getenv("MicrosoftAppTenantId", "")

settings = BotFrameworkAdapterSettings(
    app_id=APP_ID,
    app_password=APP_PASSWORD,
    channel_auth_tenant=APP_TENANT_ID
)

adapter = BotFrameworkAdapter(settings)


@app.get("/")
def root():
    return {
        "message": "EduAssist está funcionando"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }



class EduAssistBot(ActivityHandler):

    async def on_message_activity(self, turn_context: TurnContext):

        user_message = turn_context.activity.text or ""

        print(f"Mensaje recibido: {user_message}")

        await turn_context.send_activity(
            f"EduAssist recibió: {user_message}"
        )


bot = EduAssistBot()


@app.post("/api/messages")
async def messages(request: Request):

    auth_header = request.headers.get("Authorization", "")

    body = await request.json()

    activity = Activity().deserialize(body)

    print("ACTIVIDAD RECIBIDA")
    print(activity)

    response = await adapter.process_activity(
        activity,
        auth_header,
        bot.on_turn
    )

    if response:
        return Response(
            content=response.body,
            status_code=response.status,
            media_type="application/json"
        )

    return Response(status_code=201)

