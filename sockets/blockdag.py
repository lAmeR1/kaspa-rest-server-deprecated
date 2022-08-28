# encoding: utf-8

from fastapi_utils.tasks import repeat_every

from endpoints.get_blockdag import get_blockdag
from endpoints.get_circulating_supply import get_coinsupply
from server import sio, app

BLOCKS_CACHE = []


@app.on_event("startup")
@repeat_every(seconds=5)
async def emit_blockdag():
    resp = await get_blockdag()
    await sio.emit("blockdag", resp, room="blockdag")
