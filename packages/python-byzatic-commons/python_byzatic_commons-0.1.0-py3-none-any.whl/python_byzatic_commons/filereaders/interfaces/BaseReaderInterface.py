#
#
#
from abc import ABCMeta, abstractmethod


class BaseReaderInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def read(self, file: str) -> any:
        pass
