import logging

from fastapi import FastAPI, Request
from langchain_core.messages import HumanMessage

from app.config import settings
from app.orchestrator.graph import orchestrator
from app.whatsapp.client import WhatsAppClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Agent WhatsApp Orchestrator")
whatsapp = WhatsAppClient()


@app.post("/webhook/messages")
async def handle_webhook(request: Request):
    body = await request.json()

    if body.get("event") != "messages.upsert":
        return {"status": "ignored"}

    data = body.get("data", {})
    key = data.get("key", {})
    from_me = key.get("fromMe", False)
    sender = key.get("remoteJid", "")
    text = (
        data.get("message", {}).get("conversation", "")
        or data.get("message", {}).get("extendedTextMessage", {}).get("text", "")
    )
    push_name = data.get("pushName", "")

    if from_me or not sender or not text:
        return {"status": "ignored"}

    if settings.allowed_group_jid and sender != settings.allowed_group_jid:
        return {"status": "ignored"}

    logger.info("[%s] %s: %s", sender, push_name, text[:100])

    result = await orchestrator.ainvoke(
        {"messages": [HumanMessage(content=text)]}
    )

    response_text = result["messages"][-1].content
    await whatsapp.send_message(to=sender, text=response_text)

    logger.info("[%s] Reply sent", sender)
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}
