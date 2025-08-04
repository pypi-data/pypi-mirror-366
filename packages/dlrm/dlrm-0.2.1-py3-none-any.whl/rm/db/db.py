from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from turtle import pd
from typing import Dict, Generic, Type, TypeVar, cast
from typing_extensions import Self

from rm.dirtree.file_name_id_manager import File_Name_ID_Parser
from rm.tree.path_tree import PathTreeNode, PurePathTreeNode
import re



def find_db_element_paths(base_dir: Path)->list[Path]:
    # DB의 항목에 해당하는 모든 경로 반환환
    pattern = re.compile(r'^.+___id_\d+(?:\.[\w\d_-]+)?$')
    matched_paths = []

    def _walk(current_dir: Path):
        for entry in current_dir.iterdir():
            if pattern.match(entry.name):
                matched_paths.append(entry)
                # 폴더인 경우 하위 탐색 생략
                continue
            if entry.is_dir():
                _walk(entry)

    _walk(base_dir)
    return matched_paths



@dataclass
class DBTreeNode(PathTreeNode):
    root_dir:Path
    name_id_parser:File_Name_ID_Parser = field(default=File_Name_ID_Parser(), init=False)

    @property
    def path(self)->Path:
        return self.root_dir/super().path

    def terminal_nodes(self)->list[Self]:
        if self.is_terminal:
            return [self]
        else:
            return sum([child.terminal_nodes() for child in self.children], [])


    def _create_root_node(self, name:str)->Self:
        return self.__class__(name=name, _init_file_system_sync_on=self.file_system_sync_on, root_dir=self.root_dir)

    @property
    def __db_id(self)->int|None:
        id, name, ext =self.name_id_parser.split(self.path)
        return id
    
    @property
    def is_empty(self)->bool:
        return super().is_empty and (not self.__is_db_element)

    @property
    def __is_db_element(self)->bool:
        return self.__db_id is not None
    

    def pruning(self): # 빈 노드 제거
        for child in self.children:
            child.pruning()

        if self.is_root: return # root는 대상이 되지 않음 

        if self.is_empty:
            self.delete()

@dataclass
class FileSystemRecord:
    # 단일 데이터 셋, 모델 또는 작업을 관리한다.
    # 리소스에 맞게 확장된 클래스를 사용한 것으로 기대대 
    
    db:'FileSystemDB'
    id:int
    dir_path:Path

@dataclass
class DirPropertyRecord:
    db:'FileSystemDB'
    id:int
    dir_path:Path


RecordType = TypeVar("RecordType", bound=FileSystemRecord)

class ElementType(Enum):
    FILE = "file"
    DIR = "dir"

@dataclass
class FileSystemDB(Generic[RecordType]):
    # 내부적으로 tree를 이용하며, terminal node를 하나의 항목으로 다루는 클래스
    root_dir_path:Path
    RecordClass:Type[RecordType]
    element_type:ElementType

    name_id_parser:File_Name_ID_Parser = field(default=File_Name_ID_Parser(), init=False)
    
    
    def __post_init__(self):
        paths = find_db_element_paths(self.root_dir_path)
        self.__tree = DBTreeNode(name=self.root_dir_path, _init_file_system_sync_on=False, root_dir=self.root_dir_path)
        for path in paths:
            self.__tree.create(path.relative_to(self.root_dir_path))
        self.__tree.file_system_sync_on = True

    @property
    def __elements(self)->list[DBTreeNode]:
        return self.__tree.terminal_nodes()
    
    
    @property
    def __new_id(self)->int: return max(self.ids) + 1

    @property
    def __id_elements(self)->dict[str, DBTreeNode]:
        result = {}
        for element in self.__elements:
            id, name, ext = self.name_id_parser.split(element.path)
            result[id] = element
        return result

    def __get_element(self, id:str)->DBTreeNode:
        return self.__id_elements[id]


    @property
    def ids(self)->list[str]: return list(self.__id_elements.keys())    
    
    def get_record(self, id:str)->RecordType:
        element = self.__get_element(id)
        return self.RecordClass(db=self, id=id, dir_path=element.path)

    def print_tree(self):
        self.__tree.print_tree()
    
    def create(self, name:str, ext:str=None)->Self:
        new_id = self.__new_id
        new_path = self.name_id_parser.merge(new_id, name, ext)
        node = self.__tree.create(new_path)

        if self.element_type == ElementType.FILE:
            node.clear() # 폴더 데이터를 지우고 파일로 변환
            node.path.touch()

        return self.get_record(new_id)
    
    def remove(self, id:int)->Self:
        element = self.__get_element(id)
        element.parent.unlink(element.name).clear() # 자식 노드를 분리하고 삭제
        # self.root.pruning() # 빈 노드 제거


    @property
    def size(self)->int: return len(self.__elements)

    def pruning(self): self.__tree.pruning()

    def print_tree(self):
        self.__tree.print_tree()

    # @property
    # def table(self)->pd.DataFrame:
    #     id_tokens_dict:Dict[ID, list[NAME]] = {k: v.split("/") for k, v in self.db.dir_db.id_name_dict.items()}
    #     max_len = max([len(v) for v in id_tokens_dict.values()], default=0)

    #     for k, v in id_tokens_dict.items():
    #         for i in range(max_len-len(v)):
    #             v.append("")
        
    #     df = pd.DataFrame(id_tokens_dict).T.reset_index()
    #     df.rename(columns={"index": "id"}, inplace=True)

    #     return df