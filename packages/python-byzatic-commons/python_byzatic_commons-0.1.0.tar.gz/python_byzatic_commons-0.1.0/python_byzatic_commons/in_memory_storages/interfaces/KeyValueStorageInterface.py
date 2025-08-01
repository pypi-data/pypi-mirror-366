#
#
#
from abc import ABCMeta, abstractmethod
from python_byzatic_commons.crud.interfaces import KeyValueCRUDInterface


class KeyValueStorageInterface(KeyValueCRUDInterface):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self, entry_id: str, data: any) -> int:
        pass

    @abstractmethod
    def read(self, entry_id: str) -> any:
        pass

    @abstractmethod
    def update(self, entry_id: str, data: any) -> int:
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> int:
        pass

    @abstractmethod
    def drop(self) -> int:
        pass

    @abstractmethod
    def read_all(self) -> dict:
        pass

    @abstractmethod
    def read_list_keys(self) -> list:
        pass

    @abstractmethod
    def contains(self, entry_id: str) -> bool:
        pass
