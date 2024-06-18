from pydantic import BaseModel
from typing import Optional
from beanie import PydanticObjectId as ObjectId


class DashboardCreate(BaseModel):
    user_id: int
    name: str
    folder_id: Optional[ObjectId] = None
    metadata: Optional[dict] = {}


class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    folder_id: Optional[ObjectId] = None
    metadata: Optional[dict] = None


class DashboardsGet(BaseModel):
    user_id: Optional[int] = None
    folder_id: Optional[ObjectId] = None
    name: Optional[str] = None


class DashboardResponse(BaseModel):
    id: ObjectId
    user_id: int
    name: str
    folder_id: Optional[ObjectId] = None
    metadata: Optional[dict] = {}

    class Config:
        from_attributes = True