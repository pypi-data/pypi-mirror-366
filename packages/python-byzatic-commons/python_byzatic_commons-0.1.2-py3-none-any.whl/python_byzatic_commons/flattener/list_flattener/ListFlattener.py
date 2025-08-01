#
#
#
import logging

from flattener.interfaces import ListFlattenerInterface
from python_byzatic_commons.flattener.dl_flattener import DLFlattener


class ListFlattener(ListFlattenerInterface):
    def __init__(self):
        self.logger = logging.getLogger("app")
        self.__flattener: DLFlattener = DLFlattener()

    def flatten(self, data_object: list, separator: str = '.') -> dict:
        """
        Turn a nested dictionary into a flattened dictionary
        :param_name data_object: The list to flatten
        :param_name separator: The string used to separate flattened keys
        :return: A flattened dictionary
        """
        flatten_dict: dict = self.__flattener.flatten(data_object, separator)
        return flatten_dict
