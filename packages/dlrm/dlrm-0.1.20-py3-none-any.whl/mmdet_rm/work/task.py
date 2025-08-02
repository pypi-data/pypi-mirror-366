from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Type

from pydantic import Field

from mmdet_rm.settings import get_settings
from rm import ID, NAME, PropertyManager, DBView, ResourceDB, ResourceDBFactory, ResourceRecord
from rm.resource_db.base_model import AutoSavingModel
from rm.resource_db.property_manager import PathHandling_PropertyManager

if TYPE_CHECKING:
    from .work_resource import WorkRecord, WorkResourceFactory


from .command_builder import MMDetectionCommandBuilder

@dataclass
class TaskKey:
    WORK_ID:str = "work_id"
    TASK_ID:str = "task_id"
    # TASK_TYPE:str = "task_type"
    # DATASET_ID:str = "dataset_id"
    # EPOCH:str = "epoch"
    # MODEL_ID:str = "model_id"
    # CONFIG_ID:str = "config_id"

# @dataclass
class TaskConfigManager(AutoSavingModel):
    # 데이터 셋 리소스에 대한 config를 관리하는 객체체

    work_id:Optional[ID] = Field(default=None)
    task_type:Optional[Literal["train", "eval", "test"]] = Field(default=None)
    dataset_id:Optional[ID] = Field(default=None)
    epoch:Optional[int] = Field(default=None)
    model_id:Optional[ID] = Field(default=None)
    # config_id:Optional[ID] = Field(default=None)


    ################ 참조해서 가져오는 속성들들

    @property
    def config_id(self)->ID:
        from mmdet_rm.factory import get_root_factory
        return get_root_factory().work_factory.db.get(self.work_id).property_manager.config_id
    
    @property
    def mmdet_config_file_path(self)->Path:
        from mmdet_rm.factory import get_root_factory
        config_record = get_root_factory().config_factory.db.get(self.config_id)
        return config_record.file_path



@dataclass
class MMDetectionCommand:  


    def get_command(self, task_type:Literal["train", "eval", "test"], relative:bool = True)->Path:
        if task_type == "train":
            path = get_settings().train_code_path
        elif task_type == "eval":
            path = get_settings().test_code_path
        elif task_type == "test":
            path = get_settings().test_code_path
        
        if relative:
            return path.relative_to(get_settings().project_root)
        else:
            return path

@dataclass
class TaskRecord(ResourceRecord[TaskConfigManager]):
    # config_manager:TaskConfigManager
    
    cammand_file_manager = MMDetectionCommand()

    # @cached_property
    # def main_config_file_path(self)->Path:
    #     from mmdet_rm.factory import get_root_factory
    #     get_root_factory().config_factory.resource_db.get(self.property_manager.config_id)

    #     from .work_resource import WorkResourceFactory
    #     work_resource_factory:WorkResourceFactory = WorkResourceFactory()

    #     work_record:WorkRecord = work_resource_factory.resource_db.get(self.property_manager.work_id)
    #     return work_record.property_manager.config_file_path

    def make_run_command(self, relative:bool = True)->str:
        
        command_file_path = self.cammand_file_manager.get_command(self.property_manager.task_type, relative=relative)
        main_config_file_path = self.property_manager.mmdet_config_file_path
        if relative:
            main_config_file_path = main_config_file_path.relative_to(get_settings().project_root)

        options_dict={
            "--cfg-options": {
                "custom_config":{
                    TaskKey.WORK_ID:self.property_manager.work_id,
                    TaskKey.TASK_ID:self.id,
                }
            }
        }

        return MMDetectionCommandBuilder.build_mmdet_command(command_file_path, [main_config_file_path], options_dict)

    def get_dataset_config(self, dataset_id:ID)->tuple[Path, Path]:
        from ..dataset.dataset_resource import DatasetResourceFactory
        dataset_resource_factory:DatasetResourceFactory = DatasetResourceFactory()
        dataset_record = dataset_resource_factory.db.get(dataset_id)
        rpm = dataset_record.property_manager.refered_property_manager

        dataset_dir_path = rpm.dataset_dir_absolute_path
        annotation_file_path = rpm.annotation_file_absolute_path

        return dataset_dir_path, annotation_file_path

    def update_config(self, config):
        dataset_id = self.property_manager.dataset_id
        # model_id = self.config_manager.model_id
        epoch = self.property_manager.epoch


        dataset_dir_path, annotation_file_path = self.get_dataset_config(dataset_id)


        # Train 모드는 val을 포함하지 않음, 어짜피 수행 안할 것임.
        # 그러니 일단 혼돈이 없도록, 전부 학습 데이터로 세팅
        config.train_dataloader.dataset.data_root = dataset_dir_path.as_posix()
        config.train_dataloader.dataset.ann_file = annotation_file_path.as_posix()
        config.val_dataloader.dataset.ann_file = annotation_file_path.as_posix()
        config.val_dataloader.dataset.data_root = dataset_dir_path.as_posix()
        config.test_dataloader.dataset.ann_file = annotation_file_path.as_posix()
        config.test_dataloader.dataset.data_root = dataset_dir_path.as_posix()


        config.work_dir = self.dir_path.as_posix()

        return config

        # print(config)
        # print(type(config))
        # print("업데이트트")
        # exit()



class TaskDB(ResourceDB[TaskRecord]):
    pass




@dataclass
class TaskDBView(DBView):
    db:TaskDB



@dataclass
class TaskResourceFactory(ResourceDBFactory[TaskConfigManager, TaskRecord, TaskDB, TaskDBView]):
    dir_path:Path

    CONFIG_MANAGER_CLASS:Type[PropertyManager] = TaskConfigManager
    RECORD_CLASS:Type[ResourceRecord] = TaskRecord
    DB_CLASS:Type[ResourceDB] = TaskDB
    VIEW_CLASS:Type[DBView] = TaskDBView
    CONFIG_NAME:str = field(default="task_config")


    def make_record(self, id:ID, name:NAME, dir_path:Path)->TaskRecord:
        return self.RECORD_CLASS(id, name, dir_path, self.make_config_manager(dir_path))



if __name__ == "__main__":
    factory = TaskResourceFactory(Path("/home/submodules/mmdetection/resources/works/beverage_train/L10___id_5"))
    db = factory.db
    
    print(factory.view.table)
    

