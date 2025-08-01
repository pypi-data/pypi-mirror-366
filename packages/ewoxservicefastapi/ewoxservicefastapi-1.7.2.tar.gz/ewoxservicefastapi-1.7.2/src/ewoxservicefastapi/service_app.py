from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
import uvicorn
import os
import uvloop
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ewoxcore.constants.server_env import ServerEnv
from ewoxcore.service.interfaces.istartup import IStartup
from ewoxcore.service.interfaces.iservice import IService
from ewoxcore.service.service_app_base import ServiceAppBase
from ewoxcore.service.class_registry import ClassRegistry
from ewoxcore.utils.task_util import TaskUtil
from ewoxcore.message.message_args import MessageArgs
from ewoxservicefastapi.models.request_model import RequestModel
from ewoxservicefastapi.models.response_model import ResponseModel
from ewoxservicefastapi.routers import keepalive
from ewoxservicefastapi.middleware.jwt_auth import JWTAuthMiddleware

T = TypeVar('T')


class ServiceApp(ServiceAppBase):
    def __init__(self, service_name:str="", startup:IStartup=None, service:IService=None) -> None:
        """ Initializes the ServiceApp with a FastAPI instance. """
        super().__init__(service_name, startup, service)
        self._app:FastAPI = FastAPI()


    def _on_start_event(self):
        TaskUtil.create_task(self._start_async())


    def _setup_routes(self) -> None:
        ClassRegistry.register(RequestModel.__name__, RequestModel)
        ClassRegistry.register(ResponseModel.__name__, ResponseModel)
        ClassRegistry.register(MessageArgs.__name__, MessageArgs)

        self._app.include_router(keepalive.router)


    def addCors(self, origins:List[str], include_localhost:bool=False) -> None:
        """ Adds CORS middleware to the FastAPI app."""
        if isinstance(origins, str):
            raise TypeError("origins must be a list of strings.")
        
        if include_localhost:
            origins.append(r"|^https?:\/\/localhost(:[0-9]+)?$")

        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


    def addJWTAuth(self) -> None:
        """ Adds JWT authentication middleware to the FastAPI app."""
        self._app.add_middleware(JWTAuthMiddleware)


    def start(self, server_port:int = 80, debug_server_port:int=0) -> None:
        """ Starts the FastAPI server with the specified port. """
        uvloop.install()
        server_env:str = os.getenv(ServerEnv.ENVIRONMENT)
        if ((server_env == ServerEnv.DEVELOPMENT) & (debug_server_port != 0)):
            server_port = debug_server_port

        self._app.add_event_handler("startup", lambda: self._on_start_event())
        self._setup_routes()

#        uvicorn.run(self._app, host="127.0.0.1", port=server_port)
        uvicorn.run(self._app, host="0.0.0.0", port=server_port)
