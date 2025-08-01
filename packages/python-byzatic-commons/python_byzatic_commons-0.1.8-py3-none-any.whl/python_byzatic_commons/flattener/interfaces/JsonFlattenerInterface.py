#
#
#
from abc import ABCMeta, abstractmethod

from python_byzatic_commons.flattener.interfaces.FlattenerInterface import FlattenerInterface


class JsonFlattenerInterface(FlattenerInterface):
    metaclass = ABCMeta

    @abstractmethod
    def flatten(self, data: list or dict, separator: str = '.') -> dict:
        pass
