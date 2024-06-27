from models.query import Query
from errors import CustomException, ERR_INTERNAL
from beanie import PydanticObjectId as ObjectId
from typing import Optional, List
from schemas.query import QueryUpdate, QueriesGet
from motor.motor_asyncio import AsyncIOMotorClient as Session


class QueryRepository:
    session: Session = None

    async def create(self, query: Query) -> Query:
        try:
            await query.insert(session=self.session)
            return query
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error creating query: {str(e)}")

    async def get_by_id(self, query_id: ObjectId) -> Optional[Query]:
        try:
            query = await Query.get(query_id, session=self.session)
            return query
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error fetching query: {str(e)}")

    async def update(
        self, query_id: ObjectId, query_query: QueryUpdate
    ) -> Optional[Query]:
        try:
            query = await Query.get(query_id, session=self.session)
            data = {}
            for attr in query_query.model_fields_set:
                data[attr] = getattr(query_query, attr)
            await query.update({"$set": data}, session=self.session)
            return query
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error updating query: {str(e)}")

    async def delete(self, query_id: ObjectId) -> bool:
        try:
            query = await Query.get(query_id, session=self.session)
            res = await query.delete(session=self.session)
            return res.deleted_count > 0
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error deleting query: {str(e)}")

    async def get(self, query_query: QueriesGet) -> List[Query]:
        try:
            queries_query = Query.find(session=self.session)
            if query_query.connection_id:
                queries_query = queries_query.find(
                    Query.connection_id == query_query.connection_id, session=self.session
                )
            if query_query.user_id:
                queries_query = queries_query.find(
                    Query.user_id == query_query.user_id, session=self.session
                )
            if query_query.name:
                queries_query = queries_query.find(
                    Query.name == query_query.name, session=self.session
                )
            return await queries_query.to_list()
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error fetching queries: {str(e)}")
