# encoding: utf-8

from fastapi_utils.tasks import repeat_every

from endpoints.get_circulating_supply import get_coinsupply
from server import sio, app

BLOCKS_CACHE = []


@app.on_event("startup")
@repeat_every(seconds=1, wait_first=True)
async def periodic_coin_supply():
    await emit_coin_supply()


async def emit_coin_supply():
    resp = await get_coinsupply()
    await sio.emit("coinsupply", resp, room="coinsupply")
