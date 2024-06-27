from models.connection import Connection
from schemas.connection import (
    ConnectionCreate,
    ConnectionResponse,
    ConnectionsGet,
    ConnectionUpdate,
)
from beanie import PydanticObjectId as ObjectId
from errors import CustomException, ERR_CONNECTION_NOT_FOUND
from typing import Optional, List
from repositories.registry import RepositoryRegistry
from schemas.dashboard import DashboardUpdate
from configs.database import Operators


class ConnectionService:
    def __init__(
        self,
        repository: RepositoryRegistry,
    ):
        self.repo = repository

    async def create_connection(
        self, connection_query: ConnectionCreate
    ) -> ConnectionResponse:
        connection = Connection(
            name=connection_query.name,
            user_id=connection_query.user_id,
            type=connection_query.type,
            credentials=connection_query.credentials,
            variables=connection_query.variables,
        )
        created_connection = await self.repo.connection.create(connection)
        return ConnectionResponse(
            id=created_connection.id,
            name=created_connection.name,
            user_id=created_connection.user_id,
            type=created_connection.type,
            credentials=created_connection.credentials,
            variables=created_connection.variables,
            queries=[],
        )

    async def get_connection_by_id(
        self, connection_id: ObjectId
    ) -> Optional[ConnectionResponse]:
        connection = await self.repo.connection.get_by_id(connection_id)
        if not connection:
            raise CustomException(
                status_code=404,
                error_code=ERR_CONNECTION_NOT_FOUND,
                description="Could not find connection with the given id",
            )
        return connection

    async def update_connection(
        self, connection_id: ObjectId, connection_query: ConnectionUpdate
    ) -> Optional[ConnectionResponse]:
        connection = await self.repo.connection.get_by_id(connection_id)
        if not connection:
            raise CustomException(
                status_code=404,
                error_code=ERR_CONNECTION_NOT_FOUND,
                description="Could not find connection with the given id",
            )
        updated_connection = await self.repo.connection.update(
            connection_id, connection_query
        )
        return ConnectionResponse(
            id=updated_connection.id,
            name=updated_connection.name,
            user_id=updated_connection.user_id,
            type=updated_connection.type,
            credentials=updated_connection.credentials,
            variables=updated_connection.variables,
            queries=connection.queries,
        )

    async def delete_connection(self, connection_id: ObjectId) -> bool:
        connection = await self.repo.connection.get_by_id(connection_id)
        if not connection:
            raise CustomException(
                status_code=404,
                error_code=ERR_CONNECTION_NOT_FOUND,
                description="Could not find connection with the given id",
            )

        async def delete_connection_transaction(repo_registry: RepositoryRegistry):
            queries = await repo_registry.query.get(
                [
                    {
                        "name": "connection_id",
                        "value": connection_id,
                        "operator": Operators.EQ,
                    }
                ]
            )
            for query in queries:
                await repo_registry.query.delete(query.id)
                dashboards = await repo_registry.dashboard.get(
                    [
                        {
                            "name": "metadata.queries",
                            "value": {"id": str(query.id)},
                            "operator": Operators.EM,
                        }
                    ]
                )
                for dashboard in dashboards:
                    dashboard_queries = dashboard.metadata.get("queries", [])
                    dashboard_queries = [
                        q for q in dashboard_queries if q.get("id") != str(query.id)
                    ]
                    dashboard_query = DashboardUpdate(
                        metadata={"queries": dashboard_queries}
                    )
                    await repo_registry.dashboard.update(dashboard.id, dashboard_query)
            return await self.repo.connection.delete(connection_id)

        return await self.repo.transaction(delete_connection_transaction)

    async def get_connections(
        self, connections_query: ConnectionsGet
    ) -> List[ConnectionResponse]:
        filters = []
        if connections_query.user_id:
            filters.append(
                {
                    "name": "user_id",
                    "value": connections_query.user_id,
                    "operator": Operators.EQ,
                }
            )
        if connections_query.type:
            filters.append(
                {
                    "name": "type",
                    "value": connections_query.type,
                    "operator": Operators.EQ,
                }
            )
        if connections_query.name:
            filters.append(
                {
                    "name": "name",
                    "value": connections_query.name,
                    "operator": Operators.EQ,
                }
            )
        return await self.repo.connection.get(filters)
