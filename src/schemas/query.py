from pydantic import BaseModel
from typing import Optional
from beanie import PydanticObjectId as ObjectId
from pydantic import Field


class QueryCreate(BaseModel):
    name: str
    user_id: str
    connection_id: ObjectId
    metadata: Optional[dict] = {}


class QueryUpdate(BaseModel):
    user_id: str
    name: Optional[str] = None
    metadata: Optional[dict] = None


class QueriesGet(BaseModel):
    user_id: str
    name: Optional[str] = None
    connection_id: Optional[ObjectId] = None


class QueryResponse(BaseModel):
    id: ObjectId = Field(alias="_id")
    name: str
    user_id: str
    connection_id: ObjectId
    metadata: Optional[dict] = {}

    class Config:
        from_attributes = True
        populate_by_name = True


class ConnectionOnQueryResponse(BaseModel):
    id: ObjectId = Field(alias="_id")
    name: str
    user_id: str
    type: str
    credentials: Optional[dict] = {}
    variables: Optional[dict] = {}

    class Config:
        from_attributes = True
        populate_by_name = True


class QueryTypeResponse(BaseModel):
    id: ObjectId = Field(alias="_id")
    name: str
    user_id: str
    connection_id: ObjectId
    connection_type: str
    connection: ConnectionOnQueryResponse
    metadata: Optional[dict] = {}

    class Config:
        from_attributes = True
        populate_by_name = True
