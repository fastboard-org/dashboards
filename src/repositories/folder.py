from models.folder import Folder
from models.dashboard import Dashboard
from typing import List, Optional
from bson import ObjectId
from schemas.folder import FolderUpdate, FoldersGet


class FolderRepository:
    async def create(self, folder: Folder) -> Folder:
        await folder.insert()
        return folder

    async def get_by_id(self, folder_id: ObjectId) -> Optional[Folder]:
        return await Folder.get(folder_id)

    async def update(
        self, folder_id: ObjectId, folder_query: FolderUpdate
    ) -> Optional[Folder]:
        folder = await Folder.get(folder_id)
        data = {}
        for attr in folder_query.model_fields:
            data[attr] = getattr(folder_query, attr)
        if folder:
            await folder.update({"$set": data})
            return folder
        return None

    async def delete(self, folder_id: ObjectId) -> bool:
        folder = await Folder.get(folder_id)
        if folder:
            await folder.delete()
            await Dashboard.find(Dashboard.folder_id == folder_id).update(
                {"$set": {"folder_id": None}}
            )
            return True
        return False

    async def get(self, folder_query: FoldersGet) -> List[Folder]:
        folders_query = Folder.find()

        if folder_query.user_id:
            folders_query = folders_query.find(Folder.user_id == folder_query.user_id)
        if folder_query.name:
            folders_query = folders_query.find(Folder.name == folder_query.name)

        return await folders_query.to_list()
