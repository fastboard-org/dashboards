from fastapi import FastAPI
import uvicorn
from configs.settings import settings
from routers.dashboards import DashboardsRouter
from configs.database import mongodb
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Starting MongoDB connection")
    await mongodb.connect()
    yield
    print("Closing MongoDB connection")
    await mongodb.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(DashboardsRouter)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
