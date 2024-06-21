from fastapi import APIRouter
from routers.router_assistant import router_assistant
# from routers.healthcheck import router_health_check
from routers.router_runs import router_runs
from routers.router_messages import router_messages
from routers.router_vector_stores import router_vector_stores
from routers.router_vector_store_files import router_vector_store_files
from routers.router_files import router_files

router = APIRouter(prefix="/api/v2")

router.include_router(router_assistant)
router.include_router(router_runs)
router.include_router(router_messages)
router.include_router(router_vector_stores)
router.include_router(router_vector_store_files)
router.include_router(router_files)