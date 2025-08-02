from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Optional, Type, TypeVar

from pydantic import Field, PrivateAttr, field_serializer


from mmdet_rm.settings import get_settings
from rm import PropertyManager, DBView, ResourceDBFactory, ResourceRecord, ResourceDB, ID, NAME
from rm.resource_db.property_manager import PathHandling_PropertyManager
from rm.resource_db.base_model import AutoSavingModel
from typing import Generic

# 
class DatasetPropertyManager(AutoSavingModel):
    refer_id:Optional[ID] = Field(default=None, alias="refer_id")
    dataset_dir_path:Optional[Path] = Field(default=None, alias="dataset_dir_path")
    annotation_file_path:Optional[Path] = Field(default=None, alias="annotation_file_path")

    @property
    def dataset_dir_absolute_path(self)->Path:
        if self.dataset_dir_path is None:
            return None
        return self.to_absolute_path(self.dataset_dir_path)

    @property
    def annotation_file_absolute_path(self)->Path:
        if self.annotation_file_path is None:
            return None
        return self.to_absolute_path(self.annotation_file_path)

    @property
    def refered_property_manager(self)->'ReferedDatasetPropertyManager':
        return ReferedDatasetPropertyManager(self)

@dataclass
class ReferedDatasetPropertyManager:
    property_manager:DatasetPropertyManager

    @property
    def refer_manager(self)->'DatasetPropertyManager':
        from mmdet_rm.factory import get_root_factory
        if self.property_manager.refer_id is None:
            return None
        return get_root_factory().dataset_factory.db.get(self.property_manager.refer_id).property_manager

    @property
    def dataset_dir_absolute_path(self)->Any:
        value = self.property_manager.dataset_dir_absolute_path
        if value is None and self.refer_manager is not None:
            return self.refer_manager.dataset_dir_absolute_path
        return value

    @property
    def annotation_file_absolute_path(self)->Any:
        value = self.property_manager.annotation_file_absolute_path
        if value is None and self.refer_manager is not None:
            return self.refer_manager.annotation_file_absolute_path
        return value


@dataclass
class DatasetRecord(ResourceRecord[DatasetPropertyManager]):
    pass

class DatasetDB(ResourceDB[DatasetRecord]):
    
    def create(self, name:NAME)->DatasetRecord:
        record = super().create(name)
        pm = record.property_manager
        pm.refer_id = None
        pm.dataset_dir_path = None
        pm.annotation_file_path = None

        return record

class DatasetDBView(DBView):
    db:DatasetDB


@dataclass
class DatasetResourceFactory(ResourceDBFactory[DatasetPropertyManager, DatasetRecord, DatasetDB, DatasetDBView]):
    dir_path:Path = field(default_factory=lambda : get_settings().dataset_dir)
    
    CONFIG_MANAGER_CLASS:Type[AutoSavingModel] = DatasetPropertyManager
    RECORD_CLASS:Type[ResourceRecord] = DatasetRecord
    DB_CLASS:Type[ResourceDB] = DatasetDB
    VIEW_CLASS:Type[DatasetDBView] = DatasetDBView

# if __name__ == "__main__":
#     factory = DatasetResourceFactory()
#     db = factory.db
#     record = db.create("bear_v3")

#     print(record.property_manager.content)
#     # print(record.config_manager.dir_path)
#     # print(record.config_manager.annotation_file_path)