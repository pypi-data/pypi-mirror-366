from functools import cached_property
from pathlib import Path
from typing import Any, Type, TypeVar
from pydantic import BaseModel, PrivateAttr, ValidationInfo, field_serializer, field_validator
from ..memo import FileMemo

MODEL = TypeVar("MODEL", bound="AutoSavingModel")

class AutoSavingModel(BaseModel):
    _memo: FileMemo = PrivateAttr()
    _suspend_sync: bool = PrivateAttr(default=False)

    def __init__(self, **data):
        memo = data.pop("_memo")
        super().__init__(**data)
        self._memo = memo
        self._save()

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if not name.startswith("_") and not self._suspend_sync:
            self._save()

    def _save(self):
        self._memo.set(self.model_dump())

    @classmethod
    def load(cls: Type[MODEL], memo: FileMemo) -> MODEL:
        content = memo.get()
        return cls(_memo=memo, **content)

    @cached_property
    def dir_path(self)->Path:
        return self._memo.file_path.parent

    def to_absolute_path(self, path:Path)->Path:
        return self.dir_path / path

    @field_serializer("*", check_fields=False)
    def serialize_all_paths(self, value: Any):
        if isinstance(value, Path):
            value = self.to_absolute_path(value)
            value = value.as_posix()
        return value
    


    @classmethod
    @field_validator("*", mode="before")
    def parse_paths(cls, v: Any, info: ValidationInfo) -> Any:
        if info.field_name.endswith("_path") and isinstance(v, str):
            return Path(v)
        return v