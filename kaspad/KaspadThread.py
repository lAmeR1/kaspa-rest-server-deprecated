# encoding: utf-8
import queue
import threading
from queue import Queue, SimpleQueue

import grpc
from google.protobuf import json_format

from helper.Event import Event
from . import messages_pb2_grpc
from .messages_pb2 import KaspadMessage


class KaspadCommunicationError(Exception): pass

# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto

class KaspadThread(object):
    def __init__(self, kaspad_host, kaspad_port):
        # This is a sample Python script.

        self.channel = grpc.insecure_channel(f'{kaspad_host}:{kaspad_port}')
        self.stub = messages_pb2_grpc.RPCStub(self.channel)
        self.on_new_response = Event()
        self.on_new_error = Event()

        self.__queue = SimpleQueue()

        self.__thread = threading.Thread(target=self.__loop, daemon=True).start()
        self.__closing = False

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        # return
        self.__closing = True
        self.channel.close()

    def request(self, command, params=None, wait_for_response=True, timeout=5):
        if wait_for_response:
            q = Queue()

            def listener(e):
                q.put(e["resp"])

            self.on_new_response += listener
            self.__queue.put((command, params))
            try:
                resp = q.get(timeout=timeout)
                self.on_new_response -= listener
                return resp
            except queue.Empty as e:
                raise KaspadCommunicationError(str(e))

        else:
            self.__queue.put((command, params))

    def __loop(self):
        try:
            for resp in self.stub.MessageStream(self.__inbox()):
                resp = json_format.MessageToDict(resp)
                self.on_new_response(resp=resp)
        except Exception as e:
            if not (self.__closing is True and '"grpc_message":"Channel closed!"' in str(e)):
                self.on_new_error(error=e)

    def __inbox(self):
        while True:
            msg = KaspadMessage()
            cmd, params = self.__queue.get()
            msg2 = getattr(msg, cmd)
            payload = params

            if payload:
                if isinstance(payload, dict):
                    json_format.ParseDict(payload, msg2)
                if isinstance(payload, str):
                    json_format.Parse(payload, msg2)

            msg2.SetInParent()
            yield msg
