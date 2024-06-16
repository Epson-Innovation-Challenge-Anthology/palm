from fastapi import APIRouter

from api.resources.picture.routes import router as picture_router
from api.resources.theme.routes import router as theme_router

router = APIRouter(prefix="/resources", tags=["resource"])
router.include_router(router=theme_router)
router.include_router(router=picture_router)
