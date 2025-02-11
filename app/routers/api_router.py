from fastapi import APIRouter

from app.routers import auth, user, test

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(user.router)
api_router.include_router(auth.router)
api_router.include_router(test.router)
