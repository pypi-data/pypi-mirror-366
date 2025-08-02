from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
import json
import gzip
from ewoxcore.service.class_registry import ClassRegistry
from ewoxcore.utils.class_util import ClassUtil
from ewoxcore.utils.json_util import JsonUtil
from ewoxservicefastapi.models.request_model import RequestModel
from ewoxservicefastapi.proto.proto_request_model_pb2 import ProtoRequestModel

class RequestSerializer:

    @staticmethod
    def serialize(model: Any, use_compression: bool=True) -> RequestModel:
        """ Serialize a model to a RequestModel. """
        classes:List[str] = ClassUtil.get_class_names(model)

        json_data:str = JsonUtil.serializeJson64(model)

        proto_msg = ProtoRequestModel()
        proto_msg.data = json_data
        proto_msg.classes.extend(classes)

        data_binary:bytes = proto_msg.SerializeToString()

        arr:List[int] = []
        if use_compression:
            compressed_data:bytes = gzip.compress(data_binary)
            arr = list(compressed_data)
        else:
            arr = list(data_binary)
        
        data:str = json.dumps(arr)

        model:RequestModel = RequestModel(
            data=data,
            iscompressed=use_compression
        )

        return model



    @staticmethod
    def deserialize(
        request: RequestModel,
        classes: Optional[Dict[str, Type[Any]]] = None
    ) -> Optional[Any]:
        """ Deserialize a RequestModel to a model object. """
        decompressed_data: bytes
        data:bytes = bytes(json.loads(request.data))

        if request.iscompressed:
            decompressed_data = gzip.decompress(data)
        else:
            decompressed_data = data

        return RequestSerializer._deserialize_binary(
            decompressed_data,
            classes
        )


    @staticmethod
    def _deserialize_binary(
        data: bytes,
        classes: Optional[Dict[str, Type[Any]]] = None
    ) -> Optional[Any]:
        """ Deserialize binary data to a model object. """
        proto_msg = ProtoRequestModel()
        proto_msg.ParseFromString(data)

        if classes is None:
            classes = dict()

        for name in proto_msg.classes:
            classes[name] = ClassRegistry.get(name)

        class_type = next(iter(classes.values()))
        model = JsonUtil.deserialize_json64(class_type, proto_msg.data, to_object=True, force_merge=True)

        return model



if __name__ == "__main__":
    from ewoxcore.message.message_args import MessageArgs
    ClassRegistry.register(MessageArgs.__name__, MessageArgs)
    request:RequestModel = RequestSerializer.serialize(MessageArgs())

    model:MessageArgs = RequestSerializer.deserialize(request)
    print("Done!")


