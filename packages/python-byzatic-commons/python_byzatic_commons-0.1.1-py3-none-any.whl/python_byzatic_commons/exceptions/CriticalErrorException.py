#
#
#
import logging
import traceback
import sys
from python_byzatic_commons.exceptions import BaseErrorException


class CriticalErrorException(BaseErrorException):
    def __init__(self, excetion_object: BaseException):
        self.__logger = logging.getLogger("LibByzaticCommon-logger")
        self.exception_object = excetion_object
        self.__exec_stack_trace()

    def __exec_stack_trace(self):
        # Get current system exception
        ex_type, ex_value, ex_traceback = sys.exc_info()

        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)

        # Format stacktrace
        stack_trace = list()

        for trace in trace_back:
            stack_trace.append(
                "File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3])
            )

        self.__logger.error("Exception type : %s " % ex_type.__name__)
        self.__logger.error("Exception message : %s" % ex_value)
        for message in stack_trace:
            self.__logger.error("Stack trace : %s" % message)

