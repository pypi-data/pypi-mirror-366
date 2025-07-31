import atexit
import inspect
import math
import time
import traceback
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Callable, TypeVar
from unittest import TestCase

from easy_kit.measure import MEASURES

HEADERS = [
    'label', 'total (s)', 'time (%)', 'count', 'min', 'max', 'mean', 'std',
    'freq (real)',
    'freq (expect)',
    'freq (worst)',

]
TOTAL_TIME = '__total_time__'
NOT_MEASURED = '__not-measured__'

P = TypeVar('P')
R = TypeVar('R')


def _tabulate(headers: list[str], data: list[list[int | float | str]]):
    def _format(val: str | float):
        if val is None:
            return '***'
        if isinstance(val, float):
            return f'{val:3.2f}'
        if isinstance(val, int):
            return f'{val: 7d}'
        return val

    raw = [
        headers,
        *[
            list(map(_format, row))
            for row in data
        ]
    ]

    lengths = [
        max(len(raw[row][col]) for row in range(len(raw)))
        for col in range(len(headers))
    ]

    raw.insert(1, ['-' * _ for _ in lengths])

    return '\n'.join([
        '   '.join([_.ljust(l) for _, l in zip(row, lengths)])
        for row in raw
    ])


@dataclass
class TimeEntry:
    events: list[float] = field(default_factory=list)
    processed: int = 0
    values: dict[str, float | int] = field(default_factory=dict)

    def compress(self):
        if not self.events:
            return
        self.values = {
            name: reducer.reduce(self.processed, self.values.get(name, None), self.events)
            for name, reducer in MEASURES.items()
        }
        self.processed += len(self.events)
        self.events = []

    def raw_line(self, key: str, total_time: float):
        self.compress()
        return [
            key,
            self.values['sum'],
            100 * self.values['sum'] / total_time,
            self.values['count'],
            self.values['min'],
            self.values['max'],
            self.values['mean'],
            self.std,
            self.values['count'] / total_time,
            1. / self.values['mean'],
            1. / self.values['max'],
        ]

    @property
    def std(self):
        self.compress()
        s1 = self.values['sum']
        s2 = self.values['square_sum']
        n = self.values['count']
        if n == 0:
            return 0.
        squares = s2 / n - (s1 / n) ** 2
        if squares < 0:
            return 0
        return math.sqrt(squares)

    def _undefined(self, value: float):
        if len(self.events) <= 1:
            return ''
        return value


class DefaultLogger:
    debug = print
    info = print
    warning = print


class Timings:
    def __init__(self):
        self.event_per_entry_limit = 100
        self.db: dict[str, TimeEntry] = defaultdict(lambda: TimeEntry())
        self.active = False
        self.logs = False
        self.logger = DefaultLogger
        self.start_time: float = None

        self.sort_by_index: int = 1
        self.sort_reverse: bool = True

        # try:
        #     from loguru import logger
        #     self.logger = logger
        # except:
        #     pass

    @contextmanager
    def timing(self, name: str = None):
        if not self.active:
            yield
        else:
            if name is None:
                name = inspect.stack()[11].function
            start = self._before(name)
            yield
            self._after(name, start)

    def time_func_label(self, label: str):
        def wrapper[** P, R](func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> R:
                with self.timing(label):
                    return func(*args, **kwargs)

            return inner

        return wrapper

    def time_func[** P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def inner(*args, **kwargs) -> R:
            with self.timing(func.__qualname__):
                return func(*args, **kwargs)

        return inner

    # def time_func[** P, R](self, func: Callable[P, R]) -> Callable[P, R]:
    #     @wraps(func)
    #     def inner(*args: P.args, **kwargs: P.kwargs) -> R:
    #         with self.timing(func.__qualname__):
    #             return func(*args, **kwargs)
    # 
    #     return inner

    def show_timing(self):
        if not self.active:
            return
        try:
            self.logger.info('\n' + self.format_table())
        except Exception as e:
            self.logger.warning(f'Warning: {e}')
            traceback.print_exception(e)

    def raw_table(self):
        total_time = time.time() - self.start_time

        # TODO
        # columns = {
        #     name: measure.format_column(self.db)
        #     for name, measure in COLUMNS.items()
        # }
        # entries = [
        #     [v[i] for k, v in columns.items()]
        #     for i in range(len(columns['name']))
        # ]

        n = len(HEADERS)
        entries = [
            [
                TOTAL_TIME, total_time, 100., 1,
                *[.0] * (n - 4)
            ],
            *[
                entry.raw_line(key, total_time)
                for key, entry in self.db.items()
            ]
        ]
        sorted_entries = sorted(entries, key=lambda row: row[self.sort_by_index], reverse=self.sort_reverse)
        # final_entries = list(filter(lambda x: x[2] > 1e-3, sorted_entries))
        final_entries = sorted_entries
        return final_entries

    def format_table(self):
        return _tabulate(headers=HEADERS, data=self.raw_table())

    def select_column_sort_index(self, column_index: int):
        assert abs(column_index) < len(HEADERS)
        self.sort_reverse = column_index < 0
        self.sort_by_index = abs(column_index)

    def setup_timing(self, status: bool = True, logs: bool = False, sort_index: int = 2, show_at_exit: bool = True):
        if show_at_exit:
            atexit.register(show_timing)
        self.select_column_sort_index(sort_index)
        self.active = status
        self.logs = logs
        self.start_time = time.time()

        return time_func

    def tree_structure(self):
        groups = {}

        for key, entry in self.db.items():
            try:
                major, minor = key.split('.', maxsplit=1)
            except:
                major = '___'
                minor = key
            if major not in groups:
                groups[major] = {}
            groups[major][minor] = entry
        return groups

    def _before(self, name: str):
        if not self.active:
            return
        if self.logs:
            self.logger.debug(f'+ {name}')
        return time.time()

    def _after(self, name: str, start: float | None):
        if self.logs:
            self.logger.debug(f'- {name}')
        if start is not None:
            total = time.time() - start
            self.db[name].events.append(total)
            if len(self.db[name].events) >= self.event_per_entry_limit:
                self.db[name].compress()


_TIMING = Timings()
timing = _TIMING.timing
time_func = _TIMING.time_func
time_func_label = _TIMING.time_func_label
show_timing = _TIMING.show_timing
setup_timing = _TIMING.setup_timing
select_column_sort_index = _TIMING.select_column_sort_index


def get_elapsed_time():
    return time.time() - _TIMING.start_time


class TimingTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        setup_timing()
