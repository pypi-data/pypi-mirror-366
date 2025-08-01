from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Optional, Type

from pydantic import Field, field_serializer

from mmdet_rm.settings import get_settings
from rm import PropertyManager, DBView, ResourceDBFactory, ResourceRecord, ResourceDB, ID, NAME
from rm.resource_db.base_model import AutoSavingModel
from rm.resource_db.property_manager import PathHandling_PropertyManager

# @dataclass
# class MainConfig_PropertyKey:
#     MAIN_CONFIG_FILE_PATH:str = "main_config_file_path"

# @dataclass
class Config_PropertyManager(AutoSavingModel):
    # 데이터 셋 리소스에 대한 config를 관리하는 객체
    main_config_file_path:Optional[Path] = Field(default=None)

    # @field_serializer("main_config_file_path")
    # def serialize_paths(self, path: Optional[Path]) -> str:
    #     if path is None:
    #         return None
    #     return path.as_posix()


class ConfigRecord(ResourceRecord[Config_PropertyManager]):
    pass


class ConfigDB(ResourceDB[ConfigRecord]):
    
    def create(self, name:NAME)->ConfigRecord:
        # 실제로 
        record = super().create(name)
        record.property_manager.main_config_file_path = "main_config.py"
        return record

class ConfigDBView(DBView):
    db:ConfigDB


@dataclass
class MainConfig_ResourceFactory(ResourceDBFactory[Config_PropertyManager, ConfigRecord, ConfigDB, ConfigDBView]):
    dir_path:Path = field(default_factory=lambda : get_settings().config_dir)
    
    CONFIG_MANAGER_CLASS:Type[AutoSavingModel] = Config_PropertyManager
    RECORD_CLASS:Type[ResourceRecord] = ConfigRecord
    DB_CLASS:Type[ResourceDB] = ConfigDB
    VIEW_CLASS:Type[ConfigDBView] = ConfigDBView
