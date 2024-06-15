from fastapi import APIRouter

from api.resources.routes import router as resource_router
from api.users.routes import router as users_router

router = APIRouter(prefix="/api")
router.include_router(router=users_router)
router.include_router(router=resource_router)
