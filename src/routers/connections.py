from fastapi import APIRouter, Depends
from typing import List
from services.connection import ConnectionService
from beanie import PydanticObjectId as ObjectId
from schemas.connection import (
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionResponse,
    ConnectionsGet,
)
from repositories.registry import RepositoryRegistry
from configs.database import mongodb as db
from fastapi.security import APIKeyHeader

ConnectionsRouter = APIRouter(prefix="/v1/connections", tags=["connections"])

api_key_query = APIKeyHeader(name="api_key", auto_error=False)


def get_connection_service():
    repository = RepositoryRegistry(db)
    service = ConnectionService(repository)
    return service


@ConnectionsRouter.post("/", response_model=ConnectionResponse)
async def create_connection(
    connection: ConnectionCreate,
    service: ConnectionService = Depends(get_connection_service),
):
    return await service.create_connection(connection)


@ConnectionsRouter.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: ObjectId,
    user_id: str | None = None,
    api_key: str = Depends(api_key_query),
    service: ConnectionService = Depends(get_connection_service),
):
    return await service.get_connection_by_id(connection_id, user_id, api_key)


@ConnectionsRouter.get("/", response_model=List[ConnectionResponse])
async def list_connections(
    connections: ConnectionsGet = Depends(),
    service: ConnectionService = Depends(get_connection_service),
):
    return await service.get_connections(connections)


@ConnectionsRouter.patch("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: ObjectId,
    connection: ConnectionUpdate,
    service: ConnectionService = Depends(get_connection_service),
):
    return await service.update_connection(connection_id, connection)


@ConnectionsRouter.delete("/{connection_id}", response_model=bool)
async def delete_connection(
    connection_id: ObjectId,
    user_id: str,
    service: ConnectionService = Depends(get_connection_service),
):
    return await service.delete_connection(connection_id, user_id)
