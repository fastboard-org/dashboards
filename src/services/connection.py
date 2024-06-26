from repositories.connection import ConnectionRepository
from repositories.query import QueryRepository
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


class ConnectionService:
    def __init__(
        self,
        connection_repository: ConnectionRepository,
        query_repository: QueryRepository,
    ):
        self.connection_repository = connection_repository
        self.query_repository = query_repository

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
        created_connection = await self.connection_repository.create(connection)
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
        connection = await self.connection_repository.get_by_id(connection_id)
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
        connection = await self.connection_repository.get_by_id(connection_id)
        if not connection:
            raise CustomException(
                status_code=404,
                error_code=ERR_CONNECTION_NOT_FOUND,
                description="Could not find connection with the given id",
            )
        updated_connection = await self.connection_repository.update(
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
        connection = await self.connection_repository.get_by_id(connection_id)
        if not connection:
            raise CustomException(
                status_code=404,
                error_code=ERR_CONNECTION_NOT_FOUND,
                description="Could not find connection with the given id",
            )
        return await self.connection_repository.delete(connection_id)

    async def get_connections(
        self, connections_query: ConnectionsGet
    ) -> List[ConnectionResponse]:
        return await self.connection_repository.get(connections_query)
