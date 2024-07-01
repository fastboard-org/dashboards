from fastapi import APIRouter, Depends
from typing import List
from services.query import QueryService
from beanie import PydanticObjectId as ObjectId
from schemas.query import (
    QueryCreate,
    QueryUpdate,
    QueryResponse,
    QueriesGet,
)
from repositories.registry import RepositoryRegistry
from configs.database import mongodb as db


QueriesRouter = APIRouter(prefix="/v1/queries", tags=["queries"])


def get_query_service():
    repository = RepositoryRegistry(db)
    service = QueryService(repository)
    return service


@QueriesRouter.post("/", response_model=QueryResponse)
async def create_query(
    query: QueryCreate, service: QueryService = Depends(get_query_service)
):
    return await service.create_query(query)


@QueriesRouter.get("/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: ObjectId, service: QueryService = Depends(get_query_service)
):
    return await service.get_query_by_id(query_id)


@QueriesRouter.patch("/{query_id}", response_model=QueryResponse)
async def update_query(
    query_id: ObjectId,
    query: QueryUpdate,
    service: QueryService = Depends(get_query_service),
):
    return await service.update_query(query_id, query)


@QueriesRouter.delete("/{query_id}", response_model=bool)
async def delete_query(
    query_id: ObjectId, service: QueryService = Depends(get_query_service)
):
    return await service.delete_query(query_id)


@QueriesRouter.get("/", response_model=List[QueryResponse])
async def list_queries(
    queries: QueriesGet = Depends(), service: QueryService = Depends(get_query_service)
):
    return await service.get_queries(queries)
