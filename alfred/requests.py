from pydantic import BaseModel
from typing import Optional, List


class UserTokenRequest(BaseModel):
    username: str
    password: str
    authorized_pulsar_topics: Optional[List[str]]


class AnonymizeRequest(BaseModel):
    username: str
    password: str
    data: dict


class PulsarMessage(BaseModel):
    message: str or dict
