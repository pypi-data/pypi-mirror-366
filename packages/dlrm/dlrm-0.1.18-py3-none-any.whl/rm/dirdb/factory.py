
from functools import cached_property
from pathlib import Path
from rm.dirdb.dirdb import DirDB, DirTreeFactory, FileDB


class DirDBFactory:
    @cached_property
    def dir_tree_factory(self)->DirTreeFactory: return DirTreeFactory()

    def make_dirdb(self, dir_path:Path)->DirDB: return DirDB(dir_path, self.dir_tree_factory)



    def make_filedb(self, file_path:Path, ext:str)->FileDB: return FileDB(file_path, self.dir_tree_factory, ext)