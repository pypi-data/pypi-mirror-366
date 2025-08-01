#
#
#
from abc import ABCMeta, abstractmethod

from python_byzatic_commons.flattener.interfaces import FlattenerInterface


class DictionaryFlattenerInterface(FlattenerInterface):
    metaclass = ABCMeta

    @abstractmethod
    def flatten(self, data: dict, separator: str = '.') -> dict:
        pass
