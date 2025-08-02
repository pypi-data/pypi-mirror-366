from abc import ABC
from typing import Mapping, Iterator


class BaseOperation[T](Mapping[str, T], ABC):

    __dict: dict[str, T]
    operator: str
    typology: str

    def __init__(self, content: T):
        self.__dict = {
            self.operator: content
        }

    def __str__(self) -> str:
        return str(self.__dict)

    def __repr__(self) -> str:
        return repr(self.__dict)

    def __len__(self) -> int:
        return len(self.__dict)

    def __iter__(self) -> Iterator:
        return iter(self.__dict)

    def __getitem__(self, item: str) -> T:
        return self.__dict[item]

    def as_dict(self) -> dict[str, T]:
        ext_dict = self.__dict.copy()
        for k, v in ext_dict.items():
            if isinstance(v, BaseOperation):
                ext_dict[k] = v.as_dict()
            elif isinstance(v, dict):
                for k1, v1 in v.items():
                    if isinstance(v1, BaseOperation):
                        ext_dict[k][k1] = v1.as_dict()
        return ext_dict
