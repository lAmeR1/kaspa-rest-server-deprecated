# encoding: utf-8
import threading
from functools import partial

from kaspad.KaspadThread import KaspadThread


# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto

class KaspadClient(object):
    def __init__(self, kaspad_host, kaspad_port):
        self.kaspad_host = kaspad_host
        self.kaspad_port = kaspad_port

    async def request(self, command, params=None, timeout=5):
        with KaspadThread(self.kaspad_host, self.kaspad_port) as t:
            return await t.request(command, params, wait_for_response=True, timeout=timeout)

    def notify(self, command, params, callback):
        t = KaspadThread(self.kaspad_host, self.kaspad_port, async_thread=False)
        t.on_new_response += callback
        thread = threading.Thread(target=partial(t.notify, command, params, callback))
        thread.start()
