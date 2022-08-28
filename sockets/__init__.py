# encoding: utf-8

from server import sio

VALID_ROOMS = ["blocks"]


@sio.on("join-room")
async def join_room(sid, room_name):
    if room_name in VALID_ROOMS:
        sio.enter_room(sid, room_name)
