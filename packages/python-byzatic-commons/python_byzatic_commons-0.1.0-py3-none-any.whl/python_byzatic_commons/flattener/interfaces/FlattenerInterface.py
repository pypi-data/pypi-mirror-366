#
#
#
from abc import ABCMeta, abstractmethod
from configparser import ConfigParser


class FlattenerInterface():
    metaclass = ABCMeta

    @abstractmethod
    def flatten(self, data: any, separator: str = '.') -> dict:
        pass

