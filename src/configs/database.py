from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from configs.settings import settings
from models.dashboard import Dashboard
from models.folder import Folder
from models.connection import Connection
from models.query import Query
from contextlib import asynccontextmanager
from enum import Enum


class Operators(str, Enum):
    EQ = "$eq"
    GT = "$gt"
    GTE = "$gte"
    LT = "$lt"
    LTE = "$lte"
    NE = "$ne"
    IN = "$in"
    EM = "$elemMatch"


class MongoDB:
    def __init__(self):
        self.client = None
        self.database = None

    async def connect(self):
        DB_HOST = settings.DB_HOST
        DB_NAME = settings.DB_NAME
        DB_USER = settings.DB_USER
        DB_PASSWORD = settings.DB_PASSWORD

        DATABASE_URL = f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

        self.client = AsyncIOMotorClient(DATABASE_URL)
        self.database = self.client[DB_NAME]
        await init_beanie(
            self.database, document_models=[Dashboard, Folder, Connection, Query]
        )

    async def disconnect(self):
        self.client.close()

    @asynccontextmanager
    async def start_session(self):
        async with await self.client.start_session() as session:
            yield session


mongodb = MongoDB()
