
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Generic, Type

from rm.db.db import FileSystemRecord
from rm.memo.factory import MemoFactory
from rm.memo.property_memo import PropertyMemo, PropertyType


if TYPE_CHECKING:
    from rm.db.db import FileSystemDB

@dataclass
class FileSystemRecord:
    # 단일 데이터 셋, 모델 또는 작업을 관리한다.
    # 리소스에 맞게 확장된 클래스를 사용한 것으로 기대대 
    
    db:'FileSystemDB'
    id:int
    path:Path



class FileRecord(FileSystemRecord):
    pass

class DirRecord(FileSystemRecord):
    pass

@dataclass
class PropertyRecord(DirRecord, Generic[PropertyType]):
    property_class:Type[PropertyType]

    @property
    def __property_path(self)->Path:
        return self.path / "property"

    @property
    def __property_file(self)->PropertyMemo[PropertyType]:
        return MemoFactory().make_property_memo(self.__property_path, self.property_class)

    @property
    def prop(self)->PropertyType:
        return self.__property_file.get()
    
    @prop.setter
    def prop(self, property:PropertyType)->None:
        self.__property_file.set(property)


