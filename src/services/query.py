from models.query import Query
from beanie import PydanticObjectId as ObjectId
from errors import CustomException, ERR_QUERY_NOT_FOUND, ERR_CONNECTION_NOT_FOUND
from typing import Optional, List
from schemas.query import QueriesGet, QueryResponse, QueryCreate, QueryUpdate
from repositories.registry import RepositoryRegistry
from schemas.dashboard import DashboardsGet, DashboardUpdate


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

    async def get_query_by_id(self, query_id: ObjectId) -> Optional[QueryResponse]:
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

    async def get_queries(self, query_query: QueriesGet) -> List[QueryResponse]:
        queries = await self.repo.query.get(query_query)
        return queries

    async def delete_query(self, query_id: ObjectId) -> bool:
        query = await self.repo.query.get_by_id(query_id)
        if not query:
            raise CustomException(
                status_code=404,
                error_code=ERR_QUERY_NOT_FOUND,
                description="Could not find query with the given id",
            )

        async def delete_query_transaction(repo_registry: RepositoryRegistry):
            dashboards = await repo_registry.dashboard.get(
                DashboardsGet(query_id=query_id)
            )
            for dashboard in dashboards:
                dashboard_queries = dashboard.metadata.get("queries", [])
                dashboard_queries = [
                    q for q in dashboard_queries if q.get("id") != str(query_id)
                ]
                dashboard_query = DashboardUpdate(metadata={"queries": dashboard_queries})
                await repo_registry.dashboard.update(dashboard.id, dashboard_query)
            return await repo_registry.query.delete(query_id)

        return await self.repo.transaction(delete_query_transaction)
