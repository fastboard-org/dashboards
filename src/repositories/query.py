from models.query import Query
from errors import CustomException, ERR_INTERNAL
from beanie import PydanticObjectId as ObjectId
from typing import Optional, List
from schemas.query import QueryUpdate
from motor.motor_asyncio import AsyncIOMotorClient as Session
from schemas.query import FullQueryResponse


class QueryRepository:
    session: Session = None

    async def create(self, query: Query) -> Query:
        try:
            await query.insert(session=self.session)
            return query
        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error creating query: {str(e)}")

    async def get_by_id(self, query_id: ObjectId) -> Optional[FullQueryResponse]:
        try:
            pipeline = [
                {"$match": {"_id": query_id}},
                {
                    "$lookup": {
                        "from": "Connection",
                        "localField": "connection_id",
                        "foreignField": "_id",
                        "as": "connection",
                    }
                },
                {
                    "$unwind": {
                        "path": "$connection",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
                {
                    "$addFields": {
                        "connection_type": "$connection.type",
                    }
                },
                {
                    "$project": {
                        "connection": 0,
                    }
                },
            ]
            queries = await Query.aggregate(
                pipeline, projection_model=FullQueryResponse, session=self.session
            ).to_list()
            return queries[0] if queries else None

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

    async def get(self, filters: List) -> List[FullQueryResponse]:
        try:
            match_stage = {"$match": {}}
            for filter in filters:
                match_stage["$match"][filter["name"]] = {
                    filter["operator"]: filter["value"]
                }

            pipeline = [
                match_stage,
                {
                    "$lookup": {
                        "from": "Connection",
                        "localField": "connection_id",
                        "foreignField": "_id",
                        "as": "connection",
                    }
                },
                {
                    "$unwind": {
                        "path": "$connection",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
                {
                    "$addFields": {
                        "connection_type": "$connection.type",
                    }
                },
                {
                    "$project": {
                        "connection": 0,
                    }
                },
            ]
            queries = await Query.aggregate(
                pipeline, projection_model=FullQueryResponse, session=self.session
            ).to_list()
            return queries

        except Exception as e:
            raise CustomException(500, ERR_INTERNAL, f"Error fetching queries: {str(e)}")
