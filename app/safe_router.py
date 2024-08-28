# app/safe_router.py

from fastapi import APIRouter
from typing import Callable
import logging

logger = logging.getLogger(__name__)

class SafeAPIRouter(APIRouter):
    def add_api_route(self, path: str, endpoint: Callable, **kwargs):
        operation_id = kwargs.get('operation_id')
        if operation_id and len(operation_id) > 64:
            logger.warning(f"Operation ID '{operation_id}' exceeds 64 characters. It will be truncated.")
            kwargs['operation_id'] = operation_id[:64]
        super().add_api_route(path, endpoint, **kwargs)

    def get(self, path: str, *args, **kwargs):
        return self.add_api_route(path, methods=["GET"], *args, **kwargs)

    def post(self, path: str, *args, **kwargs):
        return self.add_api_route(path, methods=["POST"], *args, **kwargs)

    def put(self, path: str, *args, **kwargs):
        return self.add_api_route(path, methods=["PUT"], *args, **kwargs)

    def delete(self, path: str, *args, **kwargs):
        return self.add_api_route(path, methods=["DELETE"], *args, **kwargs)

    # Add other HTTP methods as needed...