#
# TODO: TracebackException
#
import logging
from errno import ENOTRECOVERABLE
import traceback
import sys
from python_byzatic_commons.exceptions import BaseErrorException


class ExitHandlerException(BaseErrorException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.__logger = logging.getLogger("LibByzaticCommon-ExitHandler-logger")
        if kwargs.get('errno') is not None:
            self.errno: int = kwargs.get('errno')
        else:
            # ENOTRECOVERABLE - State not recoverable
            self.errno: int = ENOTRECOVERABLE
        if kwargs.get('exception') is not None:
            self.exception: int = kwargs.get('exception')
        else:
            self.exception: None = None
        self.__exec_stack_trace_v1()
        self.__exec_exit(self.errno)

    def __exec_stack_trace_v0(self):
        """
        VIA sys
        @return:
        """
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

    def __exec_stack_trace_v1(self):
        """
        VIA traceback and logger.error()
        @return:
        """
        self.__logger.error(traceback.format_exc(limit=1))

    def __exec_stack_trace_v2(self):
        """
        VIA traceback and logger.exception()
        @return:
        """
        if self.exception is not None:
            self.__logger.exception(self.exception)

    def __exec_exit(self, errno: int):
        self.__logger.critical("Exiting with code: %s" % errno)
        sys.exit(errno)
