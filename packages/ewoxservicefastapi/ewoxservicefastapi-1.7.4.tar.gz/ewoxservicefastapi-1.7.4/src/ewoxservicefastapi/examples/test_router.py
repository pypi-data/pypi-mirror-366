from typing import Any, AnyStr, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from fastapi import APIRouter, Request, Body, status
from ewoxservicefastapi.api_factory import APIFactory
from ewoxservicefastapi.examples.test_request_args import TestRequestArgs
from ewoxservicefastapi.models.request_model import RequestModel
from ewoxservicefastapi.models.response_model import ResponseModel
from ewoxservicefastapi.route_base_handler import RouteBaseHandler
from ewoxcore.message.message_args import MessageArgs


class ItemRouter(RouteBaseHandler):
    def __init__(self):
        super().__init__()
        self._db = []  # fake in-memory DB

        # Register routes
        self._router.add_api_route(
            "/items",
            self.get_items,
            methods=["GET"]
        )
        self._router.add_api_route(
            "/items",
            self.add_item,
            methods=["POST"]
        )


    def get_items(self, params: Optional[str] = None):
        args:Optional[TestRequestArgs] = self.parse_params(TestRequestArgs, params)
        return {"items": self._db}


    def add_item(self, request: dict):
        try:
            print(request.get("body", {}))
    #        request:RequestModel = APIFactory.convert_to_request_model(item.get("body", {}))
    #        model:MessageArgs | None = self.parse_body(request.get("body", {}))
            
            request_model:RequestModel = APIFactory.convert_to_request_model(request)
            model:MessageArgs | None = self.parse_request(request_model)
            response:str = APIFactory.create_response(model)

            return response
        except Exception as e:
            self.log_error(e, "Error adding item")
            return APIFactory.create_empty_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )

# Expose only the router for main app
item_router = ItemRouter()._router