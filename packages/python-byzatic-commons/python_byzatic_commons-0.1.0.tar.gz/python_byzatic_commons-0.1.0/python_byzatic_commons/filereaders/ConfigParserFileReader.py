#
#
#
import logging
from configparser import ConfigParser

from python_byzatic_commons.exceptions import OperationIncompleteException
from python_byzatic_commons.filereaders.interfaces import BaseReaderInterface


# TODO: ConfigParser saving state
class ConfigParserFileReader(BaseReaderInterface):
    def __init__(self):
        self.logger = logging.getLogger("LibByzaticCommon-filereaders-logger")
        self.__reader: ConfigParser = ConfigParser()

    def read(self, path: str) -> ConfigParser:
        """
        read json file to Dict or List
        @param path: path to file
        @return: Dict or List if success or raise OperationIncompleteException from LibByzaticCommon.exceptions
        """
        try:
            self.logger.debug(f"read ini from file {path}")
            self.__reader.read(path)
            self.logger.debug(f"ConfigParser was read data from file")
            return self.__reader
        except FileNotFoundError as fnfe:
            raise OperationIncompleteException(fnfe.args, errno=fnfe.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)
