from pydantic import BaseModel
from typing import Optional, List
from beanie import PydanticObjectId as ObjectId
from models.connection import ConnectionType
from schemas.query import QueryResponse
from pydantic import Field


class ConnectionCreate(BaseModel):
    name: str
    user_id: int
    type: ConnectionType
    credentials: Optional[dict] = {}
    variables: Optional[dict] = {}


class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    credentials: Optional[dict] = None
    variables: Optional[dict] = None


class ConnectionsGet(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[ConnectionType] = None


class ConnectionResponse(BaseModel):
    id: ObjectId = Field(alias="_id")
    name: str
    user_id: int
    type: ConnectionType
    credentials: Optional[dict] = {}
    variables: Optional[dict] = {}
    queries: List[QueryResponse]

    class Config:
        from_attributes = True
        populate_by_name = True
