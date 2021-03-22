from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId


class User(BaseModel):
    username: str
    password: str
    viewable_by: Optional[List[str]]
    data: Optional[dict]


class UserInDB(User):
    _id: ObjectId
    date_created: datetime = Field(default_factory=datetime.utcnow)


class UserSen(BaseModel):
    root_id: str
    content: dict


class UserSenInDB(UserSen):
    _id: ObjectId
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
