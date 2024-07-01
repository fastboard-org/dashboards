from pydantic import BaseModel
from typing import List, Optional
from beanie import PydanticObjectId as ObjectId
from schemas.dashboard import DashboardResponse
from pydantic import Field


class FolderCreate(BaseModel):
    name: str
    user_id: str


class FolderUpdate(BaseModel):
    name: Optional[str]


class FoldersGet(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None


class FolderResponse(BaseModel):
    id: ObjectId = Field(alias="_id")
    name: str
    user_id: str
    dashboards: List[DashboardResponse]

    class Config:
        from_attributes = True
        populate_by_name = True
