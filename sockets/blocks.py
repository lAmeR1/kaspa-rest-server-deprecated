# encoding: utf-8
import asyncio

from server import kaspad_client, sio

BLOCKS_CACHE = []

def config():

    def on_new_block(e):
        global BLOCKS_CACHE
        BLOCKS_CACHE.append(e)
        asyncio.run(sio.emit("new-block", e, room="blocks"))
        BLOCKS_CACHE = BLOCKS_CACHE[-50:]

    kaspad_client.notify("notifyBlockAddedRequest", None, on_new_block)


@sio.on("last-blocks")
async def get_last_blocks(sid, msg):
    await sio.emit("last-blocks", BLOCKS_CACHE[-20:], to=sid)
