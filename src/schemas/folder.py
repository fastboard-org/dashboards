from pydantic import BaseModel
from typing import List, Optional
from beanie import PydanticObjectId as ObjectId
from schemas.dashboard import DashboardResponse


class FolderCreate(BaseModel):
    name: str
    user_id: int


class FolderUpdate(BaseModel):
    name: Optional[str]


class FoldersGet(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = None


class FolderResponse(BaseModel):
    id: ObjectId
    name: str
    user_id: int
    dashboards: List[DashboardResponse]

    class Config:
        from_attributes = True
