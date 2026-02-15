from pydantic import BaseModel


class MessageKey(BaseModel):
    remote_jid: str = ""
    from_me: bool = False
    id: str = ""

    class Config:
        extra = "allow"


class IncomingMessage(BaseModel):
    key: MessageKey
    message_type: str = ""
    message: str = ""
    push_name: str = ""

    class Config:
        extra = "allow"


class WebhookPayload(BaseModel):
    event: str
    instance: str = ""
    data: IncomingMessage | None = None

    class Config:
        extra = "allow"
