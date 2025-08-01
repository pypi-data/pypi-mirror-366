#
#
from python_byzatic_commons.exceptions.BaseErrorException import BaseErrorException
from errno import ENOTRECOVERABLE


class OperationIncompleteException(BaseErrorException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        if kwargs.get('errno') is not None:
            self.errno: int = kwargs.get('errno')
        else:
            # ENOTRECOVERABLE - State not recoverable
            self.errno: int = ENOTRECOVERABLE
