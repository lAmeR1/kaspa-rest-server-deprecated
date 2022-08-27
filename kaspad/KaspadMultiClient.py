# encoding: utf-8
from contextlib import suppress

from kaspad.KaspadClient import KaspadClient
# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto
from kaspad.KaspadThread import KaspadCommunicationError


class KaspadMultiClient(object):
    def __init__(self, hosts: list[str]):
        self.kaspads = [KaspadClient(*h.split(":")) for h in hosts]
        self.__default_kaspad = None  # type: KaspadClient

    async def new_default_kaspad(self):
        print('looking for new kaspad server')
        for k in self.kaspads:
            with suppress(KaspadCommunicationError):
                resp = await k.request("getInfoRequest", timeout=1)
                if resp["getInfoResponse"]["p2pId"]:
                    self.__default_kaspad = k
                    break
        else:
            raise KaspadCommunicationError('Kaspads not working.')

    async def request(self, command, params=None, timeout=5):
        if not self.__default_kaspad:
            await self.new_default_kaspad()

        try:
            return await self.__default_kaspad.request(command, params, timeout=timeout)
        except KaspadCommunicationError:
            await self.new_default_kaspad()
            return await self.__default_kaspad.request(command, params, timeout=timeout)

    def notify(self, command, params, callback):
        return self.kaspads[0].notify(command, params, callback)
