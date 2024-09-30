from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str
    APP_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str
    API_KEY: str
    PRIVATE_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
