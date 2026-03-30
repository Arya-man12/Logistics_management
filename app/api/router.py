from fastapi import APIRouter

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.hub import router as hub_router
from app.api.routes.shipment import router as shipment_router
from app.api.routes.tracking import router as tracking_router
from app.api.routes.user import router as user_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(shipment_router)
api_router.include_router(tracking_router)
api_router.include_router(hub_router)
api_router.include_router(admin_router)
