from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
import base64
import json
import gzip
import uuid
from ewoxcore.service.class_registry import ClassRegistry
from ewoxcore.utils.byte_util import ByteUtil
from ewoxcore.utils.class_util import ClassUtil
from ewoxcore.utils.json_util import JsonUtil
from ewoxservicefastapi.models.response_model import ResponseModel
from ewoxservicefastapi.proto.proto_response_model_pb2 import ProtoResponseModel

T = TypeVar("T")


class ResponseSerializer:

    @staticmethod
    def serialize(model: T, use_compression: bool=True) -> str:
        """ Serialize a model to a bytearray. """
        classes: List[str] = ClassUtil.get_class_names(model)

        json_data: str = JsonUtil.serializeJson64(model)

        proto_msg = ProtoResponseModel()
        proto_msg.data = json_data
        proto_msg.classes.extend(classes)

        data_binary:bytes = proto_msg.SerializeToString()

        arr: List[int] = []
        if use_compression:
            compressed_data: bytes = gzip.compress(data_binary)
            arr = list(compressed_data)
        else:
            arr = list(data_binary)

        data:str = json.dumps(arr)
        return data


    @staticmethod
    def deserialize(
        class_type:T,
        response: ResponseModel
    ) -> Optional[T]:
        """ Deserialize a ResponseModel to a model object. """
        decompressed_data: bytes

        if response.iscompressed:
            decompressed_data = gzip.decompress(response.data)
        else:
            decompressed_data = response.data

        return ResponseSerializer._deserialize_binary(
            class_type,
            decompressed_data
        )


    @staticmethod
    def _deserialize_binary(
        class_type:T,
        data: bytes
    ) -> Optional[T]:
        """ Deserialize binary data to a model object. """
        proto_msg = ProtoResponseModel()
        proto_msg.ParseFromString(data)

        model:Optional[T] = JsonUtil.deserialize_json64(class_type, proto_msg.data, to_object=True, force_merge=True)

        return model