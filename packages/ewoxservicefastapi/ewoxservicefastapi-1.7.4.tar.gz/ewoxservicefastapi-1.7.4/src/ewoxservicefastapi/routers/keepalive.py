from typing import Any, AnyStr, Callable, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar, Type
import jsonpickle
import logging
from fastapi import APIRouter, Request, Body, status

router = APIRouter()

async def print_request(request):
    print(f'request header       : {dict(request.headers.items())}' )
    print(f'request query params : {dict(request.query_params.items())}')  
    try : 
        json_str = await request.json()
        print(f'request json         : {await request.json()}')
    except Exception as err:
        # could not parse json
        print(f'request body         : {await request.body()}')


@router.get("/keepalive/")
@router.get("/healthcheck/")
def keepalive():
#        await print_request(request)
    return "OK"
