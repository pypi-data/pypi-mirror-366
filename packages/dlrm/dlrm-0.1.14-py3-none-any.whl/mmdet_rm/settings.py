from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class MMDetection_RM_Settings:

    project_root:Path = field(default=Path(__file__).parent.parent.parent)

    def __post_init__(self):
        self.resource_dir:Path = self.project_root / "resources"
        self.work_dir:Path = self.resource_dir / "works"
        self.dataset_dir:Path = self.resource_dir / "datasets"
        self.model_dir:Path = self.resource_dir / "models"
        self.log_dir:Path = self.resource_dir / "logs"
        self.result_dir:Path = self.resource_dir / "results"
        self.config_dir:Path = self.resource_dir / "configs"
        self.checkpoint_dir:Path = self.resource_dir / "checkpoints"
        self.tensorboard_dir:Path = self.resource_dir / "tensorboard"
        self.config_dir:Path = self.resource_dir / "configs"

        self.train_code_path:Path = self.project_root / "tools/train.py"
        self.test_code_path:Path = self.project_root / "tools/test.py"


    def to_relative_path(self, path:Path)->Path:
        return path.relative_to(self.project_root)

    def to_absolute_path(self, path:Path)->Path:
        return self.project_root / path


settings = MMDetection_RM_Settings()

def get_settings()->MMDetection_RM_Settings: return settings

def set_settings(new_settings:MMDetection_RM_Settings): global settings; settings = new_settings