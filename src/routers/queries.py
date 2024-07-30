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


QueriesRouter = APIRouter(prefix="/v1/queries", tags=["queries"])


def get_query_service():
    repository = RepositoryRegistry(db)
    service = QueryService(repository)
    return service


@QueriesRouter.post("/", response_model=QueryResponse, response_model_by_alias=False)
async def create_query(
    query: QueryCreate, service: QueryService = Depends(get_query_service)
):
    return await service.create_query(query)


@QueriesRouter.get(
    "/{query_id}", response_model=QueryTypeResponse, response_model_by_alias=False
)
async def get_query(
    query_id: ObjectId, service: QueryService = Depends(get_query_service)
):
    return await service.get_query_by_id(query_id)


@QueriesRouter.patch(
    "/{query_id}", response_model=QueryResponse, response_model_by_alias=False
)
async def update_query(
    query_id: ObjectId,
    query: QueryUpdate,
    service: QueryService = Depends(get_query_service),
):
    return await service.update_query(query_id, query)


@QueriesRouter.delete("/{query_id}", response_model=bool, response_model_by_alias=False)
async def delete_query(
    query_id: ObjectId, service: QueryService = Depends(get_query_service)
):
    return await service.delete_query(query_id)


@QueriesRouter.get(
    "/", response_model=List[QueryTypeResponse], response_model_by_alias=False
)
async def list_queries(
    queries: QueriesGet = Depends(), service: QueryService = Depends(get_query_service)
):
    return await service.get_queries(queries)
