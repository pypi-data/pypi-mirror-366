import json
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel

from easy_kit.timing import timing

UNPACK_CONFIG = {
    'use_list': False
}

type PathLike = Path | str


class MyModel(BaseModel):
    validation: ClassVar[bool] = True

    class Config:
        extra = 'forbid'
        arbitrary_types_allowed = True

    @classmethod
    def from_dict(cls, raw: dict, validate: bool = None):
        if validate is None:
            validate = MyModel.validation

        if validate:
            with timing('MyModel.from_dict[validate=True]'):
                return cls(**raw)
        else:
            with timing('MyModel.from_dict[validate=False]'):
                return cls.model_construct(**raw)

    def to_dict(self):
        return self.model_dump(mode='json')

    @classmethod
    def load(cls, path: PathLike, validate: bool = None):
        path = Path(path)
        if path.suffix.endswith('bson'):
            return cls.load_binary(path, validate)
        if path.suffix.endswith('json'):
            return cls.load_json(path, validate)

    def save(self, path: PathLike):
        path = Path(path)
        if path.suffix.endswith('bson'):
            self.save_binary(path)
        if path.suffix.endswith('json'):
            self.save_json(path)

    def save_json(self, path: PathLike):
        with Path(path).open('w') as _:
            json.dump(self.to_dict(), _)

    @classmethod
    def load_json(cls, path: PathLike, validate: bool = None):
        with Path(path).open() as _:
            raw = json.load(_)
            return cls.from_dict(raw, validate)

    # def save_binary(self, path: PathLike):
    #     import msgpack
    #
    #     with  Path(path).open('wb') as _:
    #         data = msgpack.packb(self.to_dict())
    #         _.write(data)
    #
    # @classmethod
    # def load_binary(cls, path: PathLike, validate: bool = None):
    #     import msgpack
    #
    #     with  Path(path).open('rb') as _:
    #         raw = msgpack.unpackb(_.read(), **UNPACK_CONFIG)
    #         return cls.from_dict(raw, validate)

    def clone(self, update: dict[str, Any] = None):
        item = self.model_dump()
        if update is not None:
            for key, value in update.items():
                self._my_update(item, key, value)
        return type(self)(**item)

    @staticmethod
    def _my_update(target: dict, path: str, value: Any):
        if '.' not in path:
            target[path] = value
        else:
            parts = path.split('.')
            for key in parts[:-1]:
                target = target[key]
            target[parts[-1]] = value

    def __hash__(self) -> int:
        return id(self)
