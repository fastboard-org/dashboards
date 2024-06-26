from beanie import Document
from enum import Enum


class ConnectionType(str, Enum):
    REST = "REST"
    MONGO = "MONGO"
    POSTGRES = "POSTGRES"


class Connection(Document):
    name: str
    user_id: int
    type: ConnectionType
    credentials: dict = {}
    variables: dict = {}

    class Settings:
        collection = "connections"
