from fastapi import APIRouter

from api.chat.routes import router as chat_router
from api.epson.routes import router as epson_router
from api.misc.routes import router as misc_router
from api.orbit.routes import router as orbit_router
from api.plan.routes import router as plan_router
from api.resources.routes import router as resource_router
from api.users.routes import router as users_router

router = APIRouter(prefix="/api")
router.include_router(router=users_router)
router.include_router(router=resource_router)
router.include_router(router=misc_router)
router.include_router(router=plan_router)
router.include_router(router=chat_router)
router.include_router(router=epson_router)
router.include_router(router=orbit_router)
