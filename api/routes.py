from fastapi import APIRouter

from api.users.routes import router as users_router

router = APIRouter(prefix="/api")
router.include_router(router=users_router)
