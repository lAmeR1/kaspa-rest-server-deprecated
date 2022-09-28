# encoding: utf-8

from server import sio
from sockets.blockdag import emit_blockdag
from sockets.bluescore import emit_bluescore
from sockets.coinsupply import emit_coin_supply

VALID_ROOMS = ["blocks", "coinsupply", "blockdag", "bluescore"]


@sio.on("join-room")
async def join_room(sid, room_name):
    if room_name in VALID_ROOMS:
        print(f"{sid} joining {room_name}")
        sio.enter_room(sid, room_name)

        if room_name == "blockdag":
            await emit_blockdag()

        if room_name == "coinsupply":
            await emit_coin_supply()

        if room_name == "bluescore":
            await emit_bluescore()

