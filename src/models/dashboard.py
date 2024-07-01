from beanie import Document
from pydantic import Field
from typing import Optional
from beanie import PydanticObjectId as ObjectId


class Dashboard(Document):
    user_id: str
    name: str
    folder_id: Optional[ObjectId] = None
    metadata: dict = Field(default_factory=dict)

    class Settings:
        collection = "dashboards"
        indexes = ["folder_id"]
