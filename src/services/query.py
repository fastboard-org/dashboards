from repositories.query import QueryRepository
from repositories.connection import ConnectionRepository
from models.query import Query
from beanie import PydanticObjectId as ObjectId
from errors import CustomException, ERR_QUERY_NOT_FOUND, ERR_CONNECTION_NOT_FOUND
from typing import Optional, List
from schemas.query import QueriesGet, QueryResponse, QueryCreate, QueryUpdate


class QueryService:
    def __init__(
        self,
        connection_repository: ConnectionRepository,
        query_repository: QueryRepository,
    ):
        self.query_repository = query_repository
        self.connection_repository = connection_repository

    async def create_query(self, query_query: QueryCreate) -> QueryResponse:
        connection = await self.connection_repository.get_by_id(query_query.connection_id)
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
        created_query = await self.query_repository.create(query)
        return QueryResponse(
            id=created_query.id,
            name=created_query.name,
            user_id=created_query.user_id,
            connection_id=created_query.connection_id,
            metadata=created_query.metadata,
        )

    async def get_query_by_id(self, query_id: ObjectId) -> Optional[QueryResponse]:
        query = await self.query_repository.get_by_id(query_id)
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
        query = await self.query_repository.get_by_id(query_id)
        if not query:
            raise CustomException(
                status_code=404,
                error_code=ERR_QUERY_NOT_FOUND,
                description="Could not find query with the given id",
            )

        updated_query = await self.query_repository.update(query_id, query_query)
        return updated_query

    async def get_queries(self, query_query: QueriesGet) -> List[QueryResponse]:
        queries = await self.query_repository.get(query_query)
        return queries

    async def delete_query(self, query_id: ObjectId) -> bool:
        query = await self.query_repository.get_by_id(query_id)
        if not query:
            raise CustomException(
                status_code=404,
                error_code=ERR_QUERY_NOT_FOUND,
                description="Could not find query with the given id",
            )
        return await self.query_repository.delete(query_id)
