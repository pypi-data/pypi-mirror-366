#
#
#
import logging
from typing import Union, Dict, List
from python_byzatic_commons.flattener.dl_flattener import DLFlattener
from flattener.interfaces import JsonFlattenerInterface


class JsonFlattener(JsonFlattenerInterface):
    def __init__(self):
        self.logger = logging.getLogger("app")
        self.__flattener: DLFlattener = DLFlattener()

    def flatten(self, data_object: Union[Dict, List], separator: str = '.') -> dict:
        """
        Turn a nested dictionary into a flattened dictionary
        :param_name data_object: The dictionary or list to flatten
        :param_name separator: The string used to separate flattened keys
        :return: A flattened dictionary
        """
        self.logger.debug(f"run make flatten dict from json loaded")
        self.logger.debug(f"json loaded is {data_object}")
        flatten_items = self.__flattener.flatten(data_object, separator)
        return flatten_items
