# encoding: utf-8
import os
from fastapi import HTTPException
from functools import wraps

from constants import NETWORK_TYPE


def filter_fields(response_dict, fields):
    if fields:
        return {
            k: v for k, v in response_dict.items() if k in fields
        }
    else:
        return response_dict


def sql_db_only(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not os.getenv("SQL_URI"):
            raise HTTPException(status_code=503, detail="Endpoint not available. "
                                                        "This endpoint needs a configured SQL database.")
        return await func(*args, **kwargs)

    return wrapper


def mainnet_only(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if NETWORK_TYPE != "mainnet":
            raise HTTPException(status_code=503, detail="Endpoint not available. "
                                                        "This endpoint is only available in mainnet.")
        return await func(*args, **kwargs)

    return wrapper

