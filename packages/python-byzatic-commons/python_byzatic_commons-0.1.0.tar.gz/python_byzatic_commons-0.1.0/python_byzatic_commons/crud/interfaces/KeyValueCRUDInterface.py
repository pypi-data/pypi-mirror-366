#
#
#
from abc import ABCMeta, abstractmethod


class KeyValueCRUDInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self, entry_id: any, data: any) -> any:
        pass

    @abstractmethod
    def read(self, entry_id: any) -> any:
        pass

    @abstractmethod
    def update(self, entry_id: any, data: any) -> any:
        pass

    @abstractmethod
    def delete(self, entry_id: any) -> any:
        pass

