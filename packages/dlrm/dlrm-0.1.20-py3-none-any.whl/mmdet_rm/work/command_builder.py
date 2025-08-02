from pathlib import Path
import shlex
from typing import Any

class MMDetectionCommandBuilder:
    
    @staticmethod
    def _flatten_cfg_dict(d: dict, parent_key: str = "") -> list[tuple[str, Any]]:
        """
        중첩된 dict를 'a.b.c': value 형태로 flatten
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(MMDetectionCommandBuilder._flatten_cfg_dict(v, new_key))
            else:
                items.append((new_key, v))
        return items

    @classmethod
    def build_mmdet_command(cls, script_path: Path, args_list: list, options_dict: Any = None) -> str:
        """
        필요한 인자들을 받아 완전한 CLI 형식의 MMDetection 명령어를 빌드하여 반환
        """
        command = ["python", script_path.as_posix()]  # 경로 객체도 str 처리
        command.extend(str(arg) for arg in args_list)  # Path 포함 가능성 고려

        if options_dict:
            for key, value in options_dict.items():
                if key == "--cfg-options":
                    if not isinstance(value, dict):
                        raise ValueError("--cfg-options value must be a dict")
                    # 중첩 dict flatten 후 key=value 형식으로 변환
                    flat_items = cls._flatten_cfg_dict(value)
                    cfg_str = " ".join(f"{k}={v}" for k, v in flat_items)
                    command.extend([key, cfg_str])
                elif isinstance(value, bool):
                    if value:
                        command.append(key)
                elif isinstance(value, list):
                    for v in value:
                        command.extend([key, str(v)])
                else:
                    command.extend([key, str(value)])

        return ' '.join(command)
