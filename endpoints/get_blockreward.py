# encoding: utf-8

from pydantic import BaseModel

from server import app


class BlockRewardResponse(BaseModel):
    blockreward: float = 12000132


@app.get("/info/blockreward", response_model=BlockRewardResponse | str, tags=["Kaspa network info"])
async def get_blockreward(stringOnly: bool = False):
    """
    DUMMY! Returns the current blockreward in KAS/block
    """
    if not stringOnly:
        return {
            "blockreward": 369.99
        }

    else:
        return "369.99"
