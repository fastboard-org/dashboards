from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from configs.settings import settings


class MongoDB:
    def __init__(self):
        self.client = None
        self.database = None

    async def connect(self):
        DB_HOST = settings.DB_HOST
        DB_NAME = settings.DB_NAME
        DB_USER = settings.DB_USER
        DB_PASSWORD = settings.DB_PASSWORD

        DATABASE_URL = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

        self.client = AsyncIOMotorClient(DATABASE_URL)
        self.database = self.client[DB_NAME]
        await init_beanie(self.database, document_models=[])

    async def disconnect(self):
        self.client.close()


mongodb = MongoDB()
