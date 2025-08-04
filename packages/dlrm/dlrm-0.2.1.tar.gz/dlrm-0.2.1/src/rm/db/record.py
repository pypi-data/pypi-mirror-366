
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Generic, Type

from rm.db.db import FileSystemRecord
from rm.memo.factory import MemoFactory
from rm.memo.property_memo import PropertyMemo, PropertyType


class FileRecord(FileSystemRecord):
    pass

class DirRecord(FileSystemRecord):
    pass

@dataclass
class PropertyRecord(DirRecord, Generic[PropertyType]):
    property_class:Type[PropertyType]

    @property
    def __property_path(self)->Path:
        return self.dir_path / "property"

    @property
    def __property_file(self)->PropertyMemo[PropertyType]:
        return MemoFactory().make_property_memo(self.__property_path, self.property_class)

    @property
    def prop(self)->PropertyType:
        return self.__property_file.get()
    
    @prop.setter
    def prop(self, property:PropertyType)->None:
        self.__property_file.set(property)


