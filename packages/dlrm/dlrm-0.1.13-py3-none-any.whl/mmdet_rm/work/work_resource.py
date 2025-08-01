from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
import shutil
from typing import Optional, Type

from pydantic import Field
from pydantic.functional_serializers import field_serializer

from rm.resource_db.base_model import AutoSavingModel
from rm.resource_db.property_manager import PathHandling_PropertyManager

from ..settings import get_settings
from rm import NAME, ResourceDB, ResourceDBFactory, ResourceRecord, ID, DBView
from .task import TaskDB, TaskDBView, TaskResourceFactory, TaskRecord


class Work_PropertyManager(AutoSavingModel):
    config_id:Optional[ID] = Field(default=None)



@dataclass
class WorkRecord(ResourceRecord[Work_PropertyManager]):
    # property_manager:Work_PropertyManager
    
    def __post_init__(self):
        self.__task_resource_factory:TaskResourceFactory = TaskResourceFactory(self.dir_path)

    @cached_property
    def task_db(self)->TaskDB:
        return self.__task_resource_factory.db

    @cached_property
    def task_view(self)->TaskDBView:
        return self.__task_resource_factory.view
    

    def to_relative_path(self, path:Path)->Path:
        return path.relative_to(self.dir_path)

    def exist_train_task(self)->bool:
        return self.task_db.exist(self.train_task_name)

    def create_train_task(self, train_dataset_id:ID, model_id:ID, epoch:int)->TaskRecord:
        if self.exist_train_task():
            raise ValueError(f"Train task already exists: {self.train_task_name}")
        
        task = self.task_db.create(self.train_task_name)
        
        pm = task.property_manager
        pm.work_id = self.id
        pm.task_type = "train"
        pm.dataset_id = train_dataset_id
        pm.model_id = model_id
        pm.epoch = epoch

        return task

    # CONFIG_NAME = "work_config.json"
    # dir_db:DirDB = DirDBFactory().make_dirdb

    # def __post_init__(self):
    #     self.pm:'PathManager' = PathManager(root=self)
    #     self.cppm:'CheckpointPathManager' = CheckpointPathManager(root=self)
    #     self.checkpoint_manager:'CheckpointManager' = CheckpointManager(root=self)



    # def _make_train_task(self, dir_path:Path, mmdet_config_file_path:Path, model_id:ID, dataset_id:ID, epoch:int)->TrainTask:
    #     task = TaskFactory().make_train_task(dir_path)
    #     task.config_manager.set_config({
    #         TaskConfigKey.MMDETECTION_CONFIG_FILE_PATH:mmdet_config_file_path.as_posix(),
    #         TaskConfigKey.DATASET_ID:dataset_id,
    #         TaskConfigKey.MODEL_ID:model_id,
    #         TaskConfigKey.EPOCH:epoch
    #     })

    #     return task

    # def make_train_task(self, model_id:ID, dataset_id:ID, epoch:int)->TrainTask:
    #     return self._make_train_task(self.train_task_dir(), self.pm.mmdetection_config_file_path, model_id, dataset_id, epoch)

    @cached_property
    def train_task_dir(self)->Path:
        return self.dir_path / "train"

    @cached_property
    def train_task_name(self)->NAME:
        return self.to_relative_path(self.train_task_dir).as_posix()

    def test_task_dir(self, dataset_id:ID, epoch:int)->Path:
        return self.dir_path / "test" / f"epoch_{epoch}" / f"{dataset_id}"

    # def val_task_dir(self, dataset_id:ID)->Path:
    #     return self.dir_path / "val" / f"{dataset_id}"


# @dataclass
# class WorkConfig:
#     train_dataset_id:ID
#     test_dataset_id:ID
    
    
class WorkDB(ResourceDB[WorkRecord]):
    DEFAULT_CONFIG_FILE_NAME:str = "main_config.py"
    
    def create(self, name: NAME, main_config_file_path:Optional[Path] = None, config_id:Optional[ID] = None) -> WorkRecord:
        if main_config_file_path is not None:
            if not main_config_file_path.exists():
                raise FileNotFoundError(f"Main config file not found: {main_config_file_path}")

        record = super().create(name)

        if main_config_file_path is not None:
            shutil.copy(main_config_file_path, self.DEFAULT_CONFIG_FILE_NAME)
        
        record.property_manager.config_id = config_id

        return record

class WorkDBView(DBView):
    db:WorkDB




@dataclass
class WorkResourceFactory(ResourceDBFactory[Work_PropertyManager, WorkRecord, WorkDB, WorkDBView]):
    dir_path:Path = field(default_factory=lambda : get_settings().work_dir)
    
    CONFIG_MANAGER_CLASS:Type[AutoSavingModel] = Work_PropertyManager
    RECORD_CLASS:Type[ResourceRecord] = WorkRecord
    DB_CLASS:Type[ResourceDB] = WorkDB
    VIEW_CLASS:Type[WorkDBView] = WorkDBView


    def make_task_resource_factory(self)->TaskResourceFactory:
        return TaskResourceFactory(self.dir_path)


if __name__ == "__main__":
    factory = WorkResourceFactory()
    db = factory.db
    work = db.create("test")
    # work = db.get("test")
    # print(work)
    task = work.create_train_task(1, 1, 1)

    command = task.make_run_command()
    print(command)

    
    # print(task.config_manager.config)

