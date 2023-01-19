# encoding: utf-8
from typing import List

from pydantic import BaseModel

from fastapi import Request

from server import app, kaspad_client, limiter


class BlockdagResponse(BaseModel):
    blueScore: int = 260890


@app.get("/info/virtual-chain-blue-score", response_model=BlockdagResponse, tags=["Kaspa network info"])
@limiter.limit("2/second")
async def get_virtual_selected_parent_blue_score(request: Request):
    """
    Returns the blue score of virtual selected parent
    """
    resp = await kaspad_client.request("getVirtualSelectedParentBlueScoreRequest")
    return resp["getVirtualSelectedParentBlueScoreResponse"]
