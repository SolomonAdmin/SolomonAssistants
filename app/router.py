from fastapi import APIRouter
from safe_router import SafeAPIRouter
from routers.router_assistant import router_assistant
from routers.router_runs import router_runs
from routers.router_messages import router_messages
from routers.router_vector_stores import router_vector_stores
from routers.router_vector_store_files import router_vector_store_files
from routers.router_files import router_files
from routers.router_o1 import router_o1
from routers.router_threads import router_threads
from routers.router_auth import router_auth
from routers.router_tools import tool_available_router 
from routers.router_assistant_builder_threads import router_assistant_builder_threads
from routers.router_workato import router_workato
from routers.router_teams import router_teams

router = SafeAPIRouter(prefix="/api/v2")

router.include_router(router_assistant)
router.include_router(tool_available_router)
router.include_router(router_runs)
router.include_router(router_messages)
router.include_router(router_vector_stores)
router.include_router(router_vector_store_files)
router.include_router(router_files)
router.include_router(router_o1)
router.include_router(router_threads)
router.include_router(router_auth)
router.include_router(router_assistant_builder_threads)
router.include_router(router_workato)
router.include_router(router_teams)