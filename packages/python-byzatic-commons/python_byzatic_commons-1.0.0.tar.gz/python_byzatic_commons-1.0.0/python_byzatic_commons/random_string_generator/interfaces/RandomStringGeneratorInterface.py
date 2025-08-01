#
#
#
from abc import ABCMeta, abstractmethod


class RandomStringGeneratorInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_string(self, letters_count: int, digits_count: int) -> str:
        pass

    @abstractmethod
    def get_token(self, letters_count: int) -> str:
        pass