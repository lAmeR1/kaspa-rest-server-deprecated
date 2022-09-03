# encoding: utf-8
import asyncio

from server import kaspad_client, sio

BLOCKS_CACHE = []


def config():
    def on_new_block(e):
        try:
            block_info = e["blockAddedNotification"]["block"]
        except KeyError:
            return

        global BLOCKS_CACHE
        BLOCKS_CACHE.append(block_info)
        if len(BLOCKS_CACHE) > 50:
            BLOCKS_CACHE.pop(0)

        asyncio.run(sio.emit("new-block", block_info, room="blocks"))

    kaspad_client.notify("notifyBlockAddedRequest", None, on_new_block)


@sio.on("last-blocks")
async def get_last_blocks(sid, msg):
    await sio.emit("last-blocks", BLOCKS_CACHE, to=sid)
