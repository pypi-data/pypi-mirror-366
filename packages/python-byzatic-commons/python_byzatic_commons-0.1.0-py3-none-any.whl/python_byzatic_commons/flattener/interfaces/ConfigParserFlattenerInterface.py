#
#
#
from abc import ABCMeta, abstractmethod
from configparser import ConfigParser

from python_byzatic_commons.flattener.interfaces import FlattenerInterface


class ConfigParserFlattenerInterface(FlattenerInterface):
    metaclass = ABCMeta

    @abstractmethod
    def flatten(self, data: ConfigParser, separator: str = '.') -> dict:
        pass
