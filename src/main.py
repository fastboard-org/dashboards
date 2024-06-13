from fastapi import FastAPI
import uvicorn
from settings import settings
from routers.dashboards import DashboardsRouter

app = FastAPI()
app.include_router(DashboardsRouter)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
