# encoding: utf-8

from server import sio


@sio.on("connect")
async def connect(sid, env):
    print("on connect", sid, env)


@sio.on("join-room")
async def join_room(sid, room_name):
    sio.enter_room(sid, room_name)
    print(f"{sid} joined room {room_name}")
