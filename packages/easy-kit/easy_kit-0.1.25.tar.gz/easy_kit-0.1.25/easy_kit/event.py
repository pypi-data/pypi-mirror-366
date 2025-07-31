from typing import Callable


class Event:
    IS_ENABLED = True

    @staticmethod
    def enable(status: bool = True):
        Event.IS_ENABLED = status

    def __init__(self, name: str = 'EventDefault'):
        self.name = name
        self.observer: list[Callable[[...], ...]] = []
        self.enabled = True
        self.verbose = False

    def emitter(self, *args, **kwargs):
        def _fun():
            self.emit(*args, **kwargs)

        return _fun

    def emit(self, *args, **kwargs):
        if self.enabled:
            for _ in self.observer:
                _(*args, **kwargs)

    def connect[** P, T](self, func: Callable[P, T]) -> Callable[P, T]:
        if Event.IS_ENABLED:
            self.observer.append(func)
        return func

    def observe[** P, T](self, func: Callable[P, T]) -> Callable[P, T]:
        def _fun(*args, **kwargs) -> T:
            res = func(*args, **kwargs)
            self.emit(res)
            return res

        return _fun
