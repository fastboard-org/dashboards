from repositories.connection import ConnectionRepository
from repositories.query import QueryRepository
from repositories.dashboard import DashboardRepository
from repositories.folder import FolderRepository
from typing import Callable
from configs.database import MongoDB


class RepositoryRegistry:
    def __init__(self, db: MongoDB):
        self.db = db
        self.connection = ConnectionRepository()
        self.query = QueryRepository()
        self.dashboard = DashboardRepository()
        self.folder = FolderRepository()

    async def transaction(self, fn: Callable):
        async with self.db.start_session() as session:
            self.connection.session = session
            self.query.session = session
            self.dashboard.session = session
            self.folder.session = session
            async with session.start_transaction():
                return await fn(self)
