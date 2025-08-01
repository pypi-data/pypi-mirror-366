#
#
#
from abc import ABCMeta, abstractmethod


class FlattenerInterface():
    metaclass = ABCMeta

    @abstractmethod
    def flatten(self, data: any, separator: str = '.') -> dict:
        pass

