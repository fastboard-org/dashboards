from beanie import Document


class Folder(Document):
    name: str
    user_id: str

    class Settings:
        collection = "folders"
