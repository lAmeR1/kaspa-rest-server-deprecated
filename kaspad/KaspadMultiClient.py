# encoding: utf-8
import asyncio
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
                print(f"checking: {k.kaspad_host}:{k.kaspad_port}")

                k.notify("notifyUtxosChangedRequest", {
                    "addresses": ['kaspa:qqce9s7850m0afeq075uuh5mas72456tazcs8nrc76thrdj3qdaecnynykehv']},
                         lambda x: print(f"test: {x}"))
                resp = await k.request("getInfoRequest", timeout=2)
                if resp["getInfoResponse"]["p2pId"] and resp["getInfoResponse"].get("isUtxoIndexed", False):
                    print(f"found kaspad {k.kaspad_host}:{k.kaspad_port}")
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
        if not self.__default_kaspad:
            asyncio.run(self.new_default_kaspad())

        return self.kaspads[0].notify(command, params, callback)
