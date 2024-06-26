from models.query import Query
from errors import CustomException, ERR_INTERNAL
from beanie import PydanticObjectId as ObjectId
from typing import Optional, List
from schemas.query import QueryUpdate, QueriesGet


class QueryRepository:
    async def create(self, query: Query) -> Query:
        try:
            await query.insert()
            return query
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error creating query: {str(e)}")

    async def get_by_id(self, query_id: ObjectId) -> Optional[Query]:
        try:
            query = await Query.get(query_id)
            return query
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error fetching query: {str(e)}")

    async def update(
        self, query_id: ObjectId, query_query: QueryUpdate
    ) -> Optional[Query]:
        try:
            query = await Query.get(query_id)
            data = {}
            for attr in query_query.model_fields_set:
                data[attr] = getattr(query_query, attr)
            await query.update({"$set": data})
            return query
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error updating query: {str(e)}")

    async def delete(self, query_id: ObjectId) -> bool:
        try:
            query = await Query.get(query_id)
            await query.delete()
            return True
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error deleting query: {str(e)}")

    async def get(self, query_query: QueriesGet) -> List[Query]:
        try:
            queries_query = Query.find()
            if query_query.connection_id:
                queries_query = queries_query.find(
                    Query.connection_id == query_query.connection_id
                )
            if query_query.user_id:
                queries_query = queries_query.find(Query.user_id == query_query.user_id)
            if query_query.name:
                queries_query = queries_query.find(Query.name == query_query.name)
            return await queries_query.to_list()
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error fetching queries: {str(e)}")
