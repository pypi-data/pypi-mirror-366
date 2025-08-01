import logging
import copy
from typing import Union, Dict, List
from collections.abc import MutableMapping
from python_byzatic_commons.flattener.interfaces.DLFlattenerInterface import DLFlattenerInterface
# TODO: Json Nan and Nill value and their keys shouldn't be added to final list
# TODO: Python None should be as 'key_name': None


class DLFlattener(DLFlattenerInterface):
    def __init__(self):
        self.logger = logging.getLogger("app")

    def flatten(self, ldobject: Union[Dict, List], separator: str = '.') -> dict:
        """
        Turn a nested dictionary into a flattened dictionary
        :param_name ldobject: The dictionary to flatten
        :param_name separator: The string used to separate flattened keys
        :return: A flattened dictionary
        """
        final_dict: dict = self.__flattener(ldobject, separator)
        return final_dict

    def __flattener(self, ldobject: Union[Dict, List], separator: str = '.'):
        final_dict: dict = {}
        if isinstance(ldobject, dict):
            final_dict = self.__flattener_logic(ldobject, parent_key='', separator=separator)
        elif isinstance(ldobject, list):
            for k, v in enumerate(ldobject):
                intermediate_dict: dict = self.__flattener_logic({str(k): v}, parent_key='', separator=separator)
                final_dict = self.__deep_dict_merge(intermediate_dict, final_dict)
        return final_dict

    def __flattener_logic(self, dictionary: dict, parent_key: str = '', separator: str = '.') -> dict:
        """
        Turn a nested dictionary into a flattened dictionary
        // https://github.com/ScriptSmith/socialreaper/blob/master/socialreaper/tools.py //
        :param_name dictionary: The dictionary to flatten
        :param_name parent_key: The string to prepend to dictionary's keys
        :param_name separator: The string used to separate flattened keys
        :return: A flattened dictionary
        """
        flatten_items = []
        for key, value in dictionary.items():
            self.logger.debug(f"'checking:', {key}")
            new_key = self.__parent_key_ph(parent_key, separator, key)
            if isinstance(value, MutableMapping):
                self.__instance_mutablemapping(new_key, value, flatten_items, separator)
            elif isinstance(value, list):
                self.__instance_list(new_key, value, flatten_items, separator)
            else:
                self.__instance_value(new_key, value, flatten_items)
        return dict(flatten_items)

    def __parent_key_ph(self, parent_key, separator, key):
        string: str
        if len(parent_key) == 0:
            string = key
        else:
            string = str(parent_key) + separator + key
        return string

    def __instance_dict(self, new_key, value, flatten_items, separator):
        self.logger.debug(f"{new_key}, ': dict found'")
        if not value.items():
            default_value: dict = {}
            self.logger.debug(f"'Adding key-value pair:', {new_key}, {default_value}")
            flatten_items.append((new_key, default_value))
        else:
            flatten_items.extend(self.__flattener_logic(value, new_key, separator).items())

    def __instance_mutablemapping(self, new_key, value, flatten_items, separator):
        self.logger.debug(f"{new_key}, ': dict found'")
        if not value.items():
            default_value: dict = {}
            self.logger.debug(f"'Adding key-value pair:', {new_key}, {default_value}")
            flatten_items.append((new_key, default_value))
        else:
            flatten_items.extend(self.__flattener_logic(value, new_key, separator).items())

    def __instance_list(self, new_key, value, flatten_items, separator):
        self.logger.debug(f"{new_key}, ': list found'")
        if len(value):
            for k, v in enumerate(value):
                flatten_items.extend(self.__flattener_logic({str(k): v}, new_key, separator).items())
        else:
            default_value: list = []
            self.logger.debug(f"'Adding key-value pair:', {new_key}, {default_value}")
            flatten_items.append((new_key, default_value))

    def __instance_value(self, new_key, value, flatten_items):
        self.logger.debug(f"'Adding key-value pair:', {new_key}, {value}")
        flatten_items.append((new_key, value))

    def __deep_dict_merge(self, dict_from: dict, dict_to: dict):
        dc_dict_to: dict = copy.deepcopy(dict_to)
        for ik, iv in dict_from.items():
            if ik not in dc_dict_to:
                dc_dict_to[ik] = iv
            else:
                self.logger.critical(f"dict merge error; source dict already contains {ik}")
                exit(1)
        return dc_dict_to
