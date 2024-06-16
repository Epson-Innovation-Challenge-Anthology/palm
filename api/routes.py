from fastapi import APIRouter

from api.misc.routes import router as misc_router
from api.plan.routes import router as plan_router
from api.resources.routes import router as resource_router
from api.users.routes import router as users_router

router = APIRouter(prefix="/api")
router.include_router(router=users_router)
router.include_router(router=resource_router)
router.include_router(router=misc_router)
router.include_router(router=plan_router)
