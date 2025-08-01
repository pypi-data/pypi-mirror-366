from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Optional, Type

from pydantic import Field, field_serializer

from mmdet_rm.settings import get_settings
from rm import PropertyManager, DBView, ResourceDBFactory, ResourceRecord, ResourceDB, ID, NAME
from rm.resource_db.property_manager import PathHandling_PropertyManager
from rm.resource_db.base_model import AutoSavingModel

# 
class DatasetPropertyManager(AutoSavingModel):
    dataset_dir_path:Optional[Path] = Field(default=None)
    annotation_file_path:Optional[Path] = Field(default=None)

    # @field_serializer("dataset_dir_path", "annotation_file_path")
    # def serialize_paths(self, path: Optional[Path]) -> str:
    #     if path is None:
    #         return None
    #     return path.as_posix()

class DatasetRecord(ResourceRecord[DatasetPropertyManager]):
    pass


class DatasetDB(ResourceDB[DatasetRecord]):
    
    def create(self, name:NAME)->DatasetRecord:
        record = super().create(name)
        pm = record.property_manager
        pm.dataset_dir_path = Path("data")
        pm.annotation_file_path = Path("annotation.json")

        return record

class DatasetDBView(DBView):
    db:DatasetDB


@dataclass
class DatasetResourceFactory(ResourceDBFactory[DatasetPropertyManager, DatasetRecord, DatasetDB, DatasetDBView]):
    dir_path:Path = field(default_factory=lambda : get_settings().dataset_dir)
    
    CONFIG_MANAGER_CLASS:Type[PropertyManager] = DatasetPropertyManager
    RECORD_CLASS:Type[ResourceRecord] = DatasetRecord
    DB_CLASS:Type[ResourceDB] = DatasetDB
    VIEW_CLASS:Type[DatasetDBView] = DatasetDBView

if __name__ == "__main__":
    factory = DatasetResourceFactory()
    db = factory.db
    record = db.create("bear_v3")

    print(record.property_manager.content)
    # print(record.config_manager.dir_path)
    # print(record.config_manager.annotation_file_path)