#
#
#
import logging
from configparser import ConfigParser
from flattener.interfaces import ConfigParserFlattenerInterface


class ConfigParserFlattener(ConfigParserFlattenerInterface):
    def __init__(self):
        self.logger = logging.getLogger('basic_logger')

    def flatten(self, data: ConfigParser, delimiter: str = '.') -> dict:
        flat_dict = {}
        for each_section in data.sections():
            for (each_key, each_val) in data.items(each_section):
                flat_dict_key = str(each_section) + delimiter + str(each_key)
                flat_dict[flat_dict_key] = each_val
        self.logger.debug(f"flat dict from ini is {flat_dict}")
        return flat_dict
