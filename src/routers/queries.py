from fastapi import APIRouter, Depends
from typing import List
from services.query import QueryService
from beanie import PydanticObjectId as ObjectId
from schemas.query import (
    QueryCreate,
    QueryUpdate,
    QueryResponse,
    QueriesGet,
    QueryTypeResponse,
)
from repositories.registry import RepositoryRegistry
from configs.database import mongodb as db
from fastapi.security import APIKeyHeader

QueriesRouter = APIRouter(prefix="/v1/queries", tags=["queries"])

api_key_query = APIKeyHeader(name="api_key", auto_error=False)


def get_query_service():
    repository = RepositoryRegistry(db)
    service = QueryService(repository)
    return service


@QueriesRouter.post("/", response_model=QueryResponse)
async def create_query(
    query: QueryCreate, service: QueryService = Depends(get_query_service)
):
    return await service.create_query(query)


@QueriesRouter.get("/{query_id}", response_model=QueryTypeResponse)
async def get_query(
    query_id: ObjectId,
    user_id: str | None = None,
    api_key: str = Depends(api_key_query),
    service: QueryService = Depends(get_query_service),
):
    return await service.get_query_by_id(query_id, user_id, api_key)


@QueriesRouter.patch("/{query_id}", response_model=QueryResponse)
async def update_query(
    query_id: ObjectId,
    query: QueryUpdate,
    service: QueryService = Depends(get_query_service),
):
    return await service.update_query(query_id, query)


@QueriesRouter.delete("/{query_id}", response_model=bool)
async def delete_query(
    query_id: ObjectId, user_id: str, service: QueryService = Depends(get_query_service)
):
    return await service.delete_query(query_id, user_id)


@QueriesRouter.get("/", response_model=List[QueryTypeResponse])
async def list_queries(
    queries: QueriesGet = Depends(), service: QueryService = Depends(get_query_service)
):
    return await service.get_queries(queries)
