# encoding: utf-8
import time
from datetime import datetime

from pydantic import BaseModel
from starlette.responses import PlainTextResponse

from helper.deflationary_table import DEFLATIONARY_TABLE
from server import app, kaspad_client


class HalvingResponse(BaseModel):
    next_halving_timestamp: int = 1662837270000
    next_halving_date: str = '2022-09-10 19:38:52 UTC'
    next_halving_amount: float = 155.123123


@app.get("/info/halving", response_model=HalvingResponse | str, tags=["Kaspa network info"])
async def get_halving(field: str | None = None):
    """
    Returns information about chromatic halving
    """
    resp = await kaspad_client.request("getBlockDagInfoRequest")
    daa_score = int(resp["getBlockDagInfoResponse"]["virtualDaaScore"])

    future_reward = 0
    daa_breakpoint = 0

    daa_list = sorted(DEFLATIONARY_TABLE)

    for i, to_break_score in enumerate(daa_list):
        if daa_score < to_break_score:
            future_reward = DEFLATIONARY_TABLE[daa_list[i + 1]]
            daa_breakpoint = to_break_score
            break

    next_halving_timestamp = int(time.time() + (daa_breakpoint - daa_score))

    if field == "next_halving_timestamp":
        return PlainTextResponse(content=str(next_halving_timestamp))

    elif field == "next_halving_date":
        return PlainTextResponse(content=datetime.utcfromtimestamp(next_halving_timestamp)
                                 .strftime('%Y-%m-%d %H:%M:%S UTC'))

    elif field == "next_halving_amount":
        return PlainTextResponse(content=str(future_reward))

    else:
        return {
            "next_halving_timestamp": next_halving_timestamp,
            "next_halving_date": datetime.utcfromtimestamp(next_halving_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC'),
            "next_halving_amount": future_reward
        }
