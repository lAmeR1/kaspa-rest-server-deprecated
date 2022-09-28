# encoding: utf-8

from fastapi_utils.tasks import repeat_every

from endpoints.get_virtual_chain_blue_score import get_virtual_selected_parent_blue_score
from server import sio, app

BLOCKS_CACHE = []


@app.on_event("startup")
@repeat_every(seconds=5)
async def periodical_blue_score():
    await emit_bluescore()


async def emit_bluescore():
    resp = await get_virtual_selected_parent_blue_score()
    await sio.emit("bluescore", resp, room="bluescore")
