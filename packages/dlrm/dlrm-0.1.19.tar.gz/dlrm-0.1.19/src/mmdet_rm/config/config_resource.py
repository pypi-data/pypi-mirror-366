# from dataclasses import dataclass, field
# from functools import cached_property
# from pathlib import Path
# from typing import Optional, Type

# from pydantic import Field, field_serializer

# from mmdet_rm.settings import get_settings
# from rm import PropertyManager, DBView, ResourceDBFactory, ResourceRecord, ResourceDB, ID, NAME
# from rm.resource_db.base_model import AutoSavingModel
# from rm.resource_db.property_manager import PathHandling_PropertyManager

# # @dataclass
# # class MainConfig_PropertyKey:
# #     MAIN_CONFIG_FILE_PATH:str = "main_config_file_path"

# # @dataclass
# class Config_PropertyManager(AutoSavingModel):
#     # 데이터 셋 리소스에 대한 config를 관리하는 객체
#     main_config_file_path:Optional[Path] = Field(default=None)

#     # @field_serializer("main_config_file_path")
#     # def serialize_paths(self, path: Optional[Path]) -> str:
#     #     if path is None:
#     #         return None
#     #     return path.as_posix()


# class ConfigRecord(ResourceRecord[Config_PropertyManager]):
#     pass


# class ConfigDB(ResourceDB[ConfigRecord]):
    
#     def create(self, name:NAME)->ConfigRecord:
#         # 실제로 
#         record = super().create(name)
#         record.property_manager.main_config_file_path = "main_config.py"
#         return record

# class ConfigDBView(DBView):
#     db:ConfigDB


# @dataclass
# class MainConfig_ResourceFactory(ResourceDBFactory[Config_PropertyManager, ConfigRecord, ConfigDB, ConfigDBView]):
#     dir_path:Path = field(default_factory=lambda : get_settings().config_dir)
    
#     CONFIG_MANAGER_CLASS:Type[AutoSavingModel] = Config_PropertyManager
#     RECORD_CLASS:Type[ResourceRecord] = ConfigRecord
#     DB_CLASS:Type[ResourceDB] = ConfigDB
#     VIEW_CLASS:Type[ConfigDBView] = ConfigDBView
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Generic, Optional, Type

from pydantic import Field, field_serializer

from mmdet_rm.settings import get_settings
from rm import PropertyManager, DBView, ResourceDBFactory, ResourceRecord, ResourceDB, ID, NAME
from rm.dirdb.dirdb import FileDB
from rm.dirdb.factory import DirDBFactory
from rm.resource_db.db import RESOURCE_RECORD


from omegaconf import OmegaConf, ListConfig


from mmengine.config import Config


@dataclass
class ConfigRecord:
    id:ID
    name:NAME
    file_path:Path
    db: 'ConfigDB' 

    def load(self)->dict:
        cfg = OmegaConf.load(self.file_path)

        base_ids = cfg.get("base_ids", [])
        base_ids = base_ids if base_ids is not None else []

        base_ids = base_ids if isinstance(base_ids, ListConfig|list) else [base_ids]

        cfg = Config()

        for base_id in base_ids:
            base_config = self.db.get(base_id)
            base_cfg = base_config.load()
            cfg.merge_from_dict(base_cfg._cfg_dict)

        main_cfg = Config.fromfile(self.file_path)
        cfg.merge_from_dict(main_cfg._cfg_dict)

        return cfg
    
    

@dataclass
class ConfigDB:
    # DIR_DB는 공유한 name 보장 x
    # ResourceDB는 고유한 name 보장

    dir_db: FileDB
    factory: 'Config_ResourceFactory'


    def all_ids(self)->list[ID]:
        return self.dir_db.ids

    def get(self, query: ID | NAME) -> ConfigRecord:
        id, name, dir_path = self.dir_db.get(query)
        return self.factory.make_record(id, name, dir_path)

    def get_unique_name(self, name:NAME)->NAME:
        i = 1
        origin_name = name
        while True:
            if not self.exist(name):
                return name
            name = f"{origin_name}_{i}"
            i += 1

    def create(self, name: NAME) -> ConfigRecord:
        name = self.get_unique_name(name)
        id = self.dir_db.create_new(name)
        return self.get(id)
    
    def exist(self, query: ID | NAME)->bool:
        return self.dir_db.exist(query)



@dataclass
class Config_ResourceFactory():
    dir_path:Path = field(default_factory=lambda : get_settings().config_dir)

    @cached_property
    def dir_db_factory(self)->DirDBFactory:
        return DirDBFactory()

    @cached_property
    def file_db(self)->FileDB:
        return self.dir_db_factory.make_filedb(self.dir_path, "py")
    
    @cached_property
    def db(self)->ConfigDB:
        return ConfigDB(self.file_db, self)

    def make_record(self, id:ID, name:NAME, file_path:Path)->ConfigRecord:
        return ConfigRecord(id, name, file_path, self.db)

    def view(self)->DBView:
        return DBView(self.db)
