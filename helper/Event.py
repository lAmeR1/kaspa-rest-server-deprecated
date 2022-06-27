class Event(object):
    def __init__(self):
        self.callbacks = set()
        self._lock = False

    def __call__(self, *args, **kwargs):
        if not self._lock:
            for callback in self.callbacks:
                evt_args = self.__get_evt_args(*args, **kwargs)

                callback(evt_args)

    def __add__(self, listener):
        self.callbacks.add(listener)
        return self

    def __sub__(self, listener):
        self.callbacks.remove(listener)
        return self

    def __get_evt_args(self, *args, **kwargs):
        evt_args = {u"Args": args}
        evt_args.update(kwargs)
        evt_args[u"EventObject"] = self
        return evt_args


class LockableEvent(Event):
    def lock(self):
        self._lock = True

    def unlock(self):
        self._lock = False
