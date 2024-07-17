from models.query import Query
from beanie import PydanticObjectId as ObjectId
from errors import CustomException, ERR_QUERY_NOT_FOUND, ERR_CONNECTION_NOT_FOUND
from typing import Optional, List
from schemas.query import (
    QueriesGet,
    QueryResponse,
    QueryCreate,
    QueryUpdate,
    FullQueryResponse,
)
from repositories.registry import RepositoryRegistry
from configs.database import Operators


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

    async def get_query_by_id(self, query_id: ObjectId) -> Optional[FullQueryResponse]:
        query = await self.repo.query.get_by_id(query_id)
        if not query:
            raise CustomException(
                status_code=404,
                error_code=ERR_QUERY_NOT_FOUND,
                description="Could not find query with the given id",
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

        updated_query = await self.repo.query.update(query_id, query_query)
        return updated_query

    async def get_queries(self, query_query: QueriesGet) -> List[FullQueryResponse]:
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
        return await self.repo.query.get(filters)

    async def delete_query(self, query_id: ObjectId) -> bool:
        query = await self.repo.query.get_by_id(query_id)
        if not query:
            raise CustomException(
                status_code=404,
                error_code=ERR_QUERY_NOT_FOUND,
                description="Could not find query with the given id",
            )
        return await self.repo.query.delete(query_id)
