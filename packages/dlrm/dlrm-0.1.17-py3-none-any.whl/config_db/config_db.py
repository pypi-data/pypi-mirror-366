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

@dataclass
class ConfigRecord:
    id:ID
    name:NAME
    file_path:Path
    db: 'ConfigDB' 

    def load(self)->dict:
        cfg = OmegaConf.load(self.file_path)

        refer_ids = cfg.get("base_ids", [])
        refer_ids = refer_ids if refer_ids is not None else []

        refer_ids = refer_ids if isinstance(refer_ids, ListConfig|list) else [refer_ids]

        cfg = OmegaConf.create()
        for refer_id in refer_ids:
            base_config = self.db.get(refer_id)
            cfg.update(base_config.load())

        cfg.update(OmegaConf.load(self.file_path))

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
        return self.dir_db_factory.make_filedb(self.dir_path, "yaml")
    
    @cached_property
    def db(self)->ConfigDB:
        return ConfigDB(self.file_db, self)

    def make_record(self, id:ID, name:NAME, file_path:Path)->ConfigRecord:
        return ConfigRecord(id, name, file_path, self.db)

    def view(self)->DBView:
        return DBView(self.db)
