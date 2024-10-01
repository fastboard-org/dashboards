from models.connection import Connection
from schemas.connection import (
    ConnectionCreate,
    ConnectionResponse,
    ConnectionsGet,
    ConnectionUpdate,
)
from beanie import PydanticObjectId as ObjectId
from errors import CustomException, ERR_CONNECTION_NOT_FOUND, ERR_NOT_AUTHORIZED
from typing import Optional, List
from repositories.registry import RepositoryRegistry
from configs.database import Operators
from configs.settings import settings
from lib.encryption import encrypt, decrypt


class ConnectionService:
    def __init__(
        self,
        repository: RepositoryRegistry,
    ):
        self.repo = repository

    async def create_connection(
        self, connection_query: ConnectionCreate
    ) -> ConnectionResponse:
        credentials = {}
        for key, value in connection_query.credentials.items():
            if key == "openai_api_key":
                credentials[key] = encrypt(value)
            else:
                credentials[key] = value
        connection = Connection(
            name=connection_query.name,
            user_id=connection_query.user_id,
            type=connection_query.type,
            credentials=credentials,
            variables=connection_query.variables,
        )
        created_connection = await self.repo.connection.create(connection)
        if "openai_api_key" in created_connection.credentials:
            created_connection.credentials["openai_api_key_preview"] = (
                "*" * 5 + connection_query.credentials["openai_api_key"][-4:]
            )
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
        self, connection_id: ObjectId, user_id: str, api_key: str
    ) -> Optional[ConnectionResponse]:
        connection = await self.repo.connection.get_by_id(connection_id)
        if not connection:
            raise CustomException(
                status_code=404,
                error_code=ERR_CONNECTION_NOT_FOUND,
                description="Could not find connection with the given id",
            )
        if connection.user_id != user_id and settings.API_KEY != api_key:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to access this connection",
            )
        if "openai_api_key" in connection.credentials:
            connection.credentials["openai_api_key_preview"] = (
                "*" * 5 + decrypt(connection.credentials["openai_api_key"])[-4:]
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
        if connection_query.user_id != connection.user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to update this connection",
            )
        if "openai_api_key" in connection_query.credentials:
            unencrypted_api_key = connection_query.credentials["openai_api_key"]
            connection_query.credentials["openai_api_key"] = encrypt(
                connection_query.credentials["openai_api_key"]
            )
        updated_connection = await self.repo.connection.update(
            connection_id, connection_query
        )
        if "openai_api_key" in updated_connection.credentials:
            updated_connection.credentials["openai_api_key_preview"] = (
                "*" * 5 + unencrypted_api_key[-4:]
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

    async def delete_connection(self, connection_id: ObjectId, user_id: str) -> bool:
        connection = await self.repo.connection.get_by_id(connection_id)
        if not connection:
            raise CustomException(
                status_code=404,
                error_code=ERR_CONNECTION_NOT_FOUND,
                description="Could not find connection with the given id",
            )
        if connection.user_id != user_id:
            raise CustomException(
                status_code=403,
                error_code=ERR_NOT_AUTHORIZED,
                description="You are not authorized to delete this connection",
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
        connections = await self.repo.connection.get(filters)
        for connection in connections:
            if "openai_api_key" in connection.credentials:
                connection.credentials["openai_api_key_preview"] = (
                    "*" * 5 + decrypt(connection.credentials["openai_api_key"])[-4:]
                )
        return connections
