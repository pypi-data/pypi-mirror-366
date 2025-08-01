#
#
#
import json
import logging
from typing import Union, Dict, List

from python_byzatic_commons.exceptions import OperationIncompleteException
from python_byzatic_commons.filereaders.interfaces import BaseReaderInterface


class JsonFileReader(BaseReaderInterface):
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger("LibByzaticCommon-filereaders-logger")

    def read(self, path: str) -> Union[Dict, List]:
        """
        read json file to Dict or List
        @param path: path to file
        @return: Dict or List if success or raise OperationIncompleteException from LibByzaticCommon.exceptions
        """
        try:
            with open(path, "r") as json_file:
                """
                Another option offered by Python is to use a "with" statement which will ensure 
                the file is closed when the code that uses it finishes running. 
                This holds true even if an exception is thrown.
                """
                json_object: Union[Dict, List] = json.load(json_file)
                # TODO: disabled ast.literal_eval() -> Cannot parse response.content when contains null as value
                #   ast.literal_eval() issue on a dict which has a null key value
                #   https://github.com/pycontribs/jenkinsapi/issues/780
                #   https://stackoverflow.com/questions/67230940/ast-literal-eval-on-a-dict-which-has-a-null-key-value
                # json_object: Union[Dict, List] = ast.literal_eval(json.dumps(json_object))
                self.logger.debug(f"Json data is {json_object}")
                return json_object
        except FileNotFoundError as fnfe:
            raise OperationIncompleteException(f"File not found {path}", errno=fnfe.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)
