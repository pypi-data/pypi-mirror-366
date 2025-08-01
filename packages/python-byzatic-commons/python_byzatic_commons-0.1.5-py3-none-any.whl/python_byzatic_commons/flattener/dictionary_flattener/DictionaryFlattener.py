#
#
#
import logging
from python_byzatic_commons.flattener.dl_flattener.DLFlattener import DLFlattener
from python_byzatic_commons.flattener.interfaces.DictionaryFlattenerInterface import DictionaryFlattenerInterface


class DictionaryFlattener(DictionaryFlattenerInterface):
    def __init__(self):
        self.logger = logging.getLogger("app")
        self.__flattener: DLFlattener = DLFlattener()

    def flatten(self, data_object: dict, separator: str = '.') -> dict:
        """
        Turn a nested dictionary into a flattened dictionary
        :param_name data_object: The dictionary to flatten
        :param_name separator: The string used to separate flattened keys
        :return: A flattened dictionary
        """
        flatten_dict: dict = self.__flattener.flatten(data_object, separator)
        return flatten_dict
