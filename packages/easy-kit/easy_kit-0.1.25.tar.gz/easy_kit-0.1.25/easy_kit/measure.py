from abc import abstractmethod
from typing import override, Type, TypeVar

import sys

T = TypeVar('T')


class Measure[T: float | int]:
    def __init__(self, name: str, dtype: Type[T]):
        self.name = name
        self.dtype = dtype

    @abstractmethod
    def reduce(self, count: int, current: T, updates: list[float]) -> T:
        ...

    def format_single(self, value: T):
        if self.dtype == float:
            return f'{value:.5f}'
        if self.dtype == int:
            return f'{value}'
        return value

    def format_column(self, entries: dict[str, 'TimeEntry']):
        for _ in entries.values():
            _.compress()

        raw = [
            self.format_single(_.values[self.name])
            for _ in entries.values()
        ]
        return raw


class Sum(Measure):
    def __init__(self):
        super().__init__('sum', float)

    @override
    def reduce(self, count: int, current: float, updates: list[float]) -> float:
        if current is None:
            current = 0
        return sum([current, *updates])


class Min(Measure):
    def __init__(self):
        super().__init__('min', float)

    @override
    def reduce(self, count: int, current: float, updates: list[float]) -> float:
        if current is None:
            current = sys.float_info.max
        return min([current, *updates])


class Max(Measure):
    def __init__(self):
        super().__init__('max', float)

    @override
    def reduce(self, count: int, current: float, updates: list[float]) -> float:
        if current is None:
            current = sys.float_info.min
        return max([current, *updates])


class Count(Measure):
    def __init__(self):
        super().__init__('count', int)

    @override
    def reduce(self, count: int, current: float, updates: list[int]) -> int:
        if current is None:
            current = 0
        return current + len(updates)


class SquareSum(Measure):
    def __init__(self):
        super().__init__('square_sum', float)

    @override
    def reduce(self, count: int, current: float, updates: list[float]) -> float:
        if current is None:
            current = 0
        return current + sum([_ * _ for _ in updates])


class Mean(Measure):
    def __init__(self):
        super().__init__('mean', float)

    @override
    def reduce(self, count: int, current: float, updates: list[float]) -> float:
        if current is None:
            current = 0.

        return (current * count + sum(updates)) / (count + len(updates))


class Name(Measure):
    def __init__(self):
        super().__init__('name', float)

    @override
    def reduce(self, count: int, current: float, updates: list[float]) -> float:
        return None

    def format_column(self, entries: dict[str, 'TimeEntry']):
        raw = list(entries.keys())
        return raw


MEASURES = {
    'sum': Sum(),
    'min': Min(),
    'max': Max(),
    'count': Count(),
    'square_sum': SquareSum(),
    'mean': Mean(),
}

COLUMNS = {
    'name': Name(),
    'count': Count(),
    'sum': Sum(),
    'min': Min(),
    'max': Max(),
    'mean': Mean(),
}
