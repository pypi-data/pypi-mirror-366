#
#
#
from abc import ABCMeta, abstractmethod

from python_byzatic_commons.flattener.interfaces import FlattenerInterface


class DLFlattenerInterface(FlattenerInterface):
    metaclass = ABCMeta

    @abstractmethod
    def flatten(self, data: dict or list, separator: str = '.') -> dict:
        pass
