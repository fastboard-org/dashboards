from models.query import Query
from beanie import PydanticObjectId as ObjectId
from errors import (
    CustomException,
    ERR_QUERY_NOT_FOUND,
    ERR_CONNECTION_NOT_FOUND,
    ERR_NOT_AUTHORIZED,
)
from typing import Optional, List
from schemas.query import (
    QueriesGet,
    QueryResponse,
    QueryCreate,
    QueryUpdate,
    QueryTypeResponse,
)
from repositories.registry import RepositoryRegistry
from configs.database import Operators
from configs.settings import settings
from lib.encryption import decrypt


class QueryService:
    def __init__(
        self,
        repository: RepositoryRegistry,
    ):
        self.repo = repository

    async def create_query(self, query_query: QueryCreate) -> QueryResponse:
        connection = await self.repo.connection.get_by_id(query_query.connection_id)
        if not connection:
            raise CustomException(
                status_code=404,
                error_code=ERR_CONNECTION_NOT_FOUND,
                description="Could not find connection with the given id",
            )
        if connection.user_id != query_query.user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to create a query in this connection",
            )
        query = Query(
            name=query_query.name,
            user_id=query_query.user_id,
            connection_id=query_query.connection_id,
            metadata=query_query.metadata,
        )
        created_query = await self.repo.query.create(query)
        return QueryResponse(
            id=created_query.id,
            name=created_query.name,
            user_id=created_query.user_id,
            connection_id=created_query.connection_id,
            metadata=created_query.metadata,
        )

    async def get_query_by_id(
        self, query_id: ObjectId, user_id: str, api_key: str
    ) -> Optional[QueryTypeResponse]:
        query = await self.repo.query.get_by_id(query_id)
        if not query:
            raise CustomException(
                status_code=404,
                error_code=ERR_QUERY_NOT_FOUND,
                description="Could not find query with the given id",
            )
        if query.user_id != user_id and settings.API_KEY != api_key:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to access this query",
            )
        if "openai_api_key" in query.connection.credentials:
            query.connection.credentials["openai_api_key_preview"] = (
                "*" * 5 + decrypt(query.connection.credentials["openai_api_key"])[-4:]
            )
        return query

    async def update_query(
        self, query_id, query_query: QueryUpdate
    ) -> Optional[QueryResponse]:
        query = await self.repo.query.get_by_id(query_id)
        if not query:
            raise CustomException(
                status_code=404,
                error_code=ERR_QUERY_NOT_FOUND,
                description="Could not find query with the given id",
            )
        if query.user_id != query_query.user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to update this query",
            )
        updated_query = await self.repo.query.update(query_id, query_query)
        if "openai_api_key" in updated_query.connection.credentials:
            updated_query.connection.credentials["openai_api_key_preview"] = (
                "*" * 5
                + decrypt(updated_query.connection.credentials["openai_api_key"])[-4:]
            )
        return updated_query

    async def get_queries(self, query_query: QueriesGet) -> List[QueryTypeResponse]:
        filters = []
        if query_query.connection_id:
            filters.append(
                {
                    "name": "connection_id",
                    "value": query_query.connection_id,
                    "operator": Operators.EQ,
                }
            )
        if query_query.user_id:
            filters.append(
                {
                    "name": "user_id",
                    "value": query_query.user_id,
                    "operator": Operators.EQ,
                }
            )
        if query_query.name:
            filters.append(
                {"name": "name", "value": query_query.name, "operator": Operators.EQ}
            )
        queries = await self.repo.query.get(filters)
        for query in queries:
            if "openai_api_key" in query.connection.credentials:
                query.connection.credentials["openai_api_key_preview"] = (
                    "*" * 5 + decrypt(query.connection.credentials["openai_api_key"])[-4:]
                )
        return queries

    async def delete_query(self, query_id: ObjectId, user_id: str) -> bool:
        query = await self.repo.query.get_by_id(query_id)
        if not query:
            raise CustomException(
                status_code=404,
                error_code=ERR_QUERY_NOT_FOUND,
                description="Could not find query with the given id",
            )
        if query.user_id != user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to delete this query",
            )
        return await self.repo.query.delete(query_id)
