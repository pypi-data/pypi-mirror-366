from pathlib import Path
from .memo import FileMemo
from .file_io import JsonFileIO, YamlFileIO


class MemoFactory:
    def make_file_memo(self, file_path:Path)->FileMemo:
        return FileMemo(file_path.with_suffix(".yaml"), YamlFileIO())

    # def make_file_memo(self, file_path:Path)->FileMemo:
    #     return FileMemo(file_path.with_suffix(".json"), JsonFileIO())


