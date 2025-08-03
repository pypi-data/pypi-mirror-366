from typing import Union

from faststream import context
from faststream.redis import RedisBroker, StreamSub
from faststream.redis.subscriber.asyncapi import AsyncAPISubscriber


class Subscriber:
    def __init__(self, broker: RedisBroker, **kwargs) -> None:
        self.broker = broker

        for key, value in kwargs.items():
            context.set_global(key, value)

    @classmethod
    def from_uri(cls, redis_uri: str, **kwargs) -> "Subscriber":
        return cls(broker=RedisBroker(redis_uri), **kwargs)

    def message(self, stream: Union[StreamSub, str]) -> AsyncAPISubscriber:
        return self.broker.subscriber(stream=stream)
