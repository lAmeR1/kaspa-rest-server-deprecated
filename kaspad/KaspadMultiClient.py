# encoding: utf-8
from contextlib import suppress

from kaspad.KaspadClient import KaspadClient

# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto
from kaspad.KaspadThread import KaspadCommunicationError


class KaspadMultiClient(object):
    def __init__(self, hosts: list[str]):
        self.kaspads = [KaspadClient(*h.split(":")) for h in hosts]
        self.__default_kaspad = None
        self.__new_default_kaspad()

    def __new_default_kaspad(self):
        print('looking for new kaspad server')
        for k in self.kaspads:
            with suppress(KaspadCommunicationError):
                resp = k.request("getInfoRequest", timeout=1)
                if resp["getInfoResponse"]["p2pId"]:
                    self.__default_kaspad = k
                    break
        else:
            raise KaspadCommunicationError('Kaspads not working.')

    def request(self, command, params=None):
        try:
            return self.__default_kaspad.request(command, params)
        except KaspadCommunicationError:
            self.__new_default_kaspad()
            return self.__default_kaspad.request(command, params)


    def notify(self, command, params, callback):
        try:
            return self.__default_kaspad.notify(command, params, callback)
        except KaspadCommunicationError:
            self.__new_default_kaspad()
            return self.__default_kaspad.notify(command, params, callback)
