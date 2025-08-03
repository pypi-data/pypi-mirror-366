from typing import Optional

from faststream.redis import RedisBroker, StreamSub
from pydantic import PositiveInt

from approck_messaging.models.message import TransportMessage


class Publisher:
    def __init__(self, broker: RedisBroker, stream: str, maxlen: Optional[PositiveInt] = None) -> None:
        self.broker = broker
        self.publisher = self.broker.publisher(stream=StreamSub(stream=stream, maxlen=maxlen))

    @classmethod
    def from_uri(cls, redis_uri: str, stream: str, maxlen: Optional[PositiveInt] = None) -> "Publisher":
        return cls(broker=RedisBroker(redis_uri), stream=stream, maxlen=maxlen)

    async def send_message(self, message: TransportMessage) -> None:
        await self.publisher.publish(message)
