from fastapi import APIRouter

from app.api.v1.routes import health, tasks, user, project

api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(health.router)
api_router.include_router(user.router)
api_router.include_router(tasks.router)
api_router.include_router(project.router)
