from beanie import Document


class Folder(Document):
    name: str
    user_id: int

    class Settings:
        collection = "folders"
