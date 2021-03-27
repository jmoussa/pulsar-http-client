from fastapi import APIRouter

from alfred.api.auth import router as auth_router
from alfred.api.pulsar import router as pulsar_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(pulsar_router)
