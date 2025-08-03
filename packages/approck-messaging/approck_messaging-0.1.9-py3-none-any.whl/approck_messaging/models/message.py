import datetime
import enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, HttpUrl


class MessageType(str, enum.Enum):
    GENERIC = "generic"
    VIDEO_NOTE = "video_note"


class MessageButton(BaseModel):
    label: str
    url: Optional[HttpUrl] = None
    callback_data: Optional[str] = None
    web_app: Optional[str] = None


class MessageMedia(BaseModel):
    id: str
    name: str
    url: HttpUrl
    type: str
    status: str


class Message(BaseModel):
    type: MessageType

    # Generic
    caption: Optional[str] = None
    media: Optional[List[MessageMedia]] = None
    buttons: Optional[List[MessageButton]] = None

    # Video Note
    video_note: Optional[MessageMedia] = None


class TransportMessageRecipient(BaseModel):
    telegram_id: int


class TransportMessage(Message):
    recipient: TransportMessageRecipient
    extra: Optional[Dict[str, Any]] = None

    valid_until: Optional[datetime.datetime] = None
