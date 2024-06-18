from fastapi import FastAPI
import uvicorn
from configs.settings import settings
from routers.dashboards import DashboardsRouter
from routers.folders import FoldersRouter
from configs.database import mongodb
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from errors import CustomException, handle_validation_error, handle_custom_exception


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Starting MongoDB connection")
    await mongodb.connect()
    yield
    print("Closing MongoDB connection")
    await mongodb.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(DashboardsRouter)
app.include_router(FoldersRouter)
app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(CustomException, handle_custom_exception)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
