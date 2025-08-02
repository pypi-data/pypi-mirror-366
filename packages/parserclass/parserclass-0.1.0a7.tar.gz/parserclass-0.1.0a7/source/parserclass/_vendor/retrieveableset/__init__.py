# SPDX-License-Identifier: MIT
from collections.abc import Iterator, Sequence
from itertools import islice
from typing import Generic, Hashable, TypeVar
H = TypeVar('H', bound=Hashable)

class RetrievableSet(Generic[H]):

    def __init__(self, data: Sequence[H] | Iterator[H]=()):
        self._data_: dict[int, H] = {hash(item): item for item in data}

    def __len__(self) -> int:
        return len(self._data_)

    def __getitem__(self, index: int) -> H:
        if index < 0:
            index = len(self._data_) + index
        return next(islice(self._data_.values(), index, None))

    def __delitem__(self, index: int) -> None:
        item = self[index]
        del self._data_[hash(item)]

    def __contains__(self, item: Hashable) -> bool:
        return hash(item) in self._data_

    def __iter__(self) -> Iterator[H]:
        return iter(self._data_.values())

    def __reversed__(self):
        return iter(reversed(self._data_.values()))

    def __repr__(self) -> str:
        return repr(self._data_.values())

    def index(self, value: H, start: int=0, stop: int | None=None):
        if start is not None and start < 0:
            start = max(len(self._data_) + start, 0)
        if stop is not None and stop < 0:
            stop += len(self._data_)
        i = start
        while stop is None or i < stop:
            try:
                v = self._data_[i]
            except IndexError:
                break
            if v is value or v == value:
                return i
            i += 1
        raise ValueError

    def pop(self, index: int=-1) -> H:
        item = self[index]
        del self[index]
        return item

    def add(self, item: H) -> None:
        self._data_[hash(item)] = item

    def get(self, item: Hashable) -> H:
        return self._data_[hash(item)]

    def popitem(self, item: H=None) -> H:
        return self._data_.pop(hash(item))