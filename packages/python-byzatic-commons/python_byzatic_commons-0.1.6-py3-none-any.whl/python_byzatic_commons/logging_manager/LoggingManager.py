# ========= How to use =========
# DEBUG / INFO / WARNING / ERROR / CRITICAL
# DEBUG - Detailed information, typically of interest only when diagnosing problems.
# INFO - Confirmation that things are working as expected.
# WARNING - An indication that something unexpected happened, or indicative of some problem
# in the near future (e.g. ‘disk space low’). The software is still working as expected.
# ERROR - Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL - A serious error, indicating that the program itself may be unable to continue running.
#
import sys
import logging
from logging.config import dictConfig, fileConfig
from python_byzatic_commons.filereaders.JsonFileReader import JsonFileReader
from python_byzatic_commons.filereaders.YamlFileReader import YamlFileReader
from python_byzatic_commons.exceptions.OperationIncompleteException import OperationIncompleteException
from python_byzatic_commons.logging_manager.interfaces.LoggingManagerInterface import LoggingManagerInterface


class LoggingManager(LoggingManagerInterface):
    def __init__(self):
        self.__configuration = dict()
        try:
            self.logger = logging.getLogger("root")
            self.__json_reader = JsonFileReader()
            self.__yaml_reader = YamlFileReader()
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    # Use Yaml __logger config
    def __setup_yaml(self, file: str) -> None:
        try:
            config_data = self.__yaml_reader.read(file)
            self.__setup_dict(config_data)
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    # Use Json __logger config
    def __setup_json(self, file: str) -> None:
        try:
            config_data = self.__json_reader.read(file)
            self.__setup_dict(config_data)
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    # Use InI __logger config
    def __setup_ini(self, file: str) -> None:
        try:
            fileConfig(file)
            self.logger.debug(f"Logger config successfully updated")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    # Use default __logger config
    def __setup_dict(self, configuration) -> None:
        try:
            if configuration is not None:
                dictConfig(configuration)
            else:
                raise OperationIncompleteException(f"Dictionary logger configuration is not set")
            self.logger.debug(f"Logger config successfully updated")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    # Configure __logger
    def init_logging(self, configuration_file: str, configuration_type: str, configuration_dict: dict = None) -> None:
        """
        Logging initialisation
        :param configuration_file: configuration file path
        :param configuration_type: INI / JSON / YAML / DICT
        :param configuration_dict: some dict with logging configuration, by default {}
        :return: None
        """
        try:
            if configuration_type == "INI":
                self.__setup_ini(configuration_file)
            elif configuration_type == "JSON":
                self.__setup_json(configuration_file)
            elif configuration_type == "YAML":
                self.__setup_yaml(configuration_file)
            elif configuration_type == "DICT":
                self.__setup_dict(configuration_dict)
            else:
                raise OperationIncompleteException(f"Unexpected configuration type: {configuration_type}")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)
