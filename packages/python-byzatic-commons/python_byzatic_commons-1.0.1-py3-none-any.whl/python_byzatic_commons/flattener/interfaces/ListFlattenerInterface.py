#
#
#
from abc import ABCMeta, abstractmethod

from python_byzatic_commons.flattener.interfaces.FlattenerInterface import FlattenerInterface


class ListFlattenerInterface(FlattenerInterface):
    metaclass = ABCMeta

    @abstractmethod
    def flatten(self, data: list, separator: str = '.') -> dict:
        pass
