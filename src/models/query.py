from beanie import Document
from beanie import PydanticObjectId as ObjectId
from pydantic import Field


class Query(Document):
    name: str
    user_id: str
    connection_id: ObjectId
    metadata: dict = Field(default_factory=dict)

    class Settings:
        collection = "queries"
        indexes = ["connection_id"]
