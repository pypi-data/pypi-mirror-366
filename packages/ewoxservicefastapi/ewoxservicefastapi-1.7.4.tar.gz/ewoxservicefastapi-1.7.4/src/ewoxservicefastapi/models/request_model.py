from typing import Any, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
from datetime import date, datetime, timedelta
import uuid


class RequestModel:
    def __init__(self, data: str="", iscompressed: bool=False, correlationid: str="") -> None:
        self.data:str = data
        self.iscompressed:bool = iscompressed
        self.correlationid:str = correlationid if correlationid != "" else str(uuid.uuid4())
