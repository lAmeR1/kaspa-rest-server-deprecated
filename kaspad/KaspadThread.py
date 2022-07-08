# encoding: utf-8
import asyncio

import grpc
from google.protobuf import json_format

from helper.Event import Event
from . import messages_pb2_grpc
from .messages_pb2 import KaspadMessage


class KaspadCommunicationError(Exception): pass


# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto

class KaspadThread(object):
    def __init__(self, kaspad_host, kaspad_port):

        self.kaspad_host = kaspad_host
        self.kaspad_port = kaspad_port

        self.channel = grpc.aio.insecure_channel(f'{kaspad_host}:{kaspad_port}')
        self.stub = messages_pb2_grpc.RPCStub(self.channel)
        self.on_new_response = Event()
        self.on_new_error = Event()

        self.__queue = asyncio.queues.Queue()

        self.__closing = False

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        self.__closing = True

    async def request(self, command, params=None, wait_for_response=True, timeout=5):
        if wait_for_response:
            try:
                async for resp in self.stub.MessageStream(self.yield_cmd(command, params), timeout=timeout):
                    self.__queue.put_nowait("done")
                    return json_format.MessageToDict(resp)
            except grpc.aio._call.AioRpcError as e:
                raise KaspadCommunicationError(str(e))

    async def yield_cmd(self, cmd, params=None):
        msg = KaspadMessage()
        msg2 = getattr(msg, cmd)
        payload = params

        if payload:
            if isinstance(payload, dict):
                json_format.ParseDict(payload, msg2)
            if isinstance(payload, str):
                json_format.Parse(payload, msg2)

        msg2.SetInParent()
        yield msg
        await self.__queue.get()
