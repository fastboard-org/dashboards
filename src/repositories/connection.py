from models.connection import Connection
from errors import CustomException, ERR_INTERNAL
from beanie import PydanticObjectId as ObjectId
from typing import Optional, List
from schemas.connection import (
    ConnectionUpdate,
    ConnectionsGet,
)
from models.query import Query
from configs.database import mongodb as db
from schemas.connection import ConnectionResponse


class ConnectionRepository:
    async def create(self, connection: Connection) -> Connection:
        try:
            await connection.insert()
            return connection
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error creating connection: {str(e)}"
            )

    async def get_by_id(self, connection_id: ObjectId) -> Optional[ConnectionResponse]:
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "Query",
                        "localField": "_id",
                        "foreignField": "connection_id",
                        "as": "queries",
                    }
                },
                {"$match": {"_id": connection_id}},
            ]
            connections = await Connection.aggregate(
                pipeline, projection_model=ConnectionResponse
            ).to_list()
            return connections[0] if connections else None
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error fetching connection: {str(e)}"
            )

    async def update(
        self, connection_id: ObjectId, connection_query: ConnectionUpdate
    ) -> Optional[Connection]:
        try:
            connection = await Connection.get(connection_id)
            data = {}
            for attr in connection_query.model_fields_set:
                data[attr] = getattr(connection_query, attr)
            await connection.update({"$set": data})
            return connection
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error updating connection: {str(e)}"
            )

    async def delete(self, connection_id: ObjectId) -> bool:
        try:
            connection = await Connection.get(connection_id)
            async with db.start_transaction() as session:
                await Query.find(Query.connection_id == connection_id).delete(
                    session=session
                )
                await connection.delete(session=session)
            return True
        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error deleting connection: {str(e)}"
            )

    async def get(self, connection_query: ConnectionsGet) -> List[ConnectionResponse]:
        try:
            match_stage = {"$match": {}}

            if connection_query.user_id:
                match_stage["$match"]["user_id"] = connection_query.user_id
            if connection_query.type:
                match_stage["$match"]["type"] = connection_query.type
            if connection_query.name:
                match_stage["$match"]["name"] = connection_query.name

            pipeline = [
                match_stage,
                {
                    "$lookup": {
                        "from": "Query",
                        "localField": "_id",
                        "foreignField": "connection_id",
                        "as": "queries",
                    }
                },
            ]

            connections = await Connection.aggregate(
                pipeline, projection_model=ConnectionResponse
            ).to_list()
            return connections

        except Exception as e:
            raise CustomException(
                500, ERR_INTERNAL, f"Error fetching connections: {str(e)}"
            )
