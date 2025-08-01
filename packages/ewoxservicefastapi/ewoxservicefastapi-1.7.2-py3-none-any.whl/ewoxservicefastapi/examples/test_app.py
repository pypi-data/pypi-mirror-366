from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
import uuid
from ewoxcore.utils.json_util import JsonUtil
from ewoxservicefastapi.examples import test_router
from ewoxservicefastapi.examples.test_request_args import TestRequestArgs
from ewoxservicefastapi.service_app import ServiceApp


class TestApp(ServiceApp):
    def __init__(self):
        super().__init__()


    async def on_start(self) -> None:
        args = TestRequestArgs()
        json_str = JsonUtil.serializeJson64(args)
        print(json_str)
        self._app.include_router(test_router.item_router) #, prefix="/item", tags=["item"])


    async def on_stop(self) -> None:
        pass


if __name__ == "__main__":
    from ewoxservicefastapi.models.request_model import RequestModel
    from ewoxservicefastapi.models.response_model import ResponseModel
    from ewoxservicefastapi.api_factory import APIFactory
    from ewoxcore.message.message_args import MessageArgs
    from ewoxservicefastapi.response_serializer import ResponseSerializer
    from ewoxcore.client.http_client import HTTPClient

    # args = MessageArgs("Dude")
    # client = HTTPClient()
    # session = client.session(120)
    # model:RequestModel = APIFactory.create_request(args)
    # json_data = JsonUtil.serialize(model)
    # data = {"body": json_data }
    # response = session.get("http://localhost:8803/match", params=data)
    # json_text = response.text
    # response_model:ResponseModel = JsonUtil.deserialize_gen_object(ResponseModel, json_text)

    print(str(uuid.uuid4()))

    app = TestApp()
    app.start(debug_server_port=8802)
