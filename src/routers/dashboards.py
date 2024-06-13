from fastapi import APIRouter

DashboardsRouter = APIRouter(prefix="/v1/dashboards", tags=["dashboards"])


@DashboardsRouter.get("/")
def hello_dashboards():
    return "Hello from dashboards! :D"
