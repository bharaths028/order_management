from fastapi import APIRouter
from .customers import router as customers_router
from .products import router as products_router
from .enquiries import router as enquiries_router
from .changelog import router as changelog_router

router = APIRouter()
router.include_router(customers_router, prefix="/customers", tags=["customers"])
router.include_router(products_router, prefix="/products", tags=["products"])
router.include_router(enquiries_router, prefix="/enquiries", tags=["enquiries"])
router.include_router(changelog_router, prefix="/changelog", tags=["changelog"])
