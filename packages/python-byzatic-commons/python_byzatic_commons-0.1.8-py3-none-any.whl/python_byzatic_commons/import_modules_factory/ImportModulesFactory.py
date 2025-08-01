#
#
#
# You can use importlib but I wont;
# import importlib
# module = importlib.import_module(module_name, package=None)
#
# TODO: for the future
# https://stackoverflow.com/questions/301134/how-can-i-import-a-module-dynamically-given-its-name-as-string
#
# Similar as @monkut 's solution but reusable and error tolerant described
# here http://stamat.wordpress.com/dynamic-module-import-in-python/:
#
# import os
# import imp
#
# def importFromURI(uri, absl):
#     mod = None
#     if not absl:
#         uri = os.path.normpath(os.path.join(os.path.dirname(__file__), uri))
#     path, fname = os.path.split(uri)
#     mname, ext = os.path.splitext(fname)
#
#     if os.path.exists(os.path.join(path,mname)+'.pyc'):
#         try:
#             return imp.load_compiled(mname, uri)
#         except:
#             pass
#     if os.path.exists(os.path.join(path,mname)+'.py'):
#         try:
#             return imp.load_source(mname, uri)
#         except:
#             pass
#
#     return mod

import logging
from types import ModuleType
from python_byzatic_commons.exceptions.OperationIncompleteException import OperationIncompleteException
from python_byzatic_commons.import_modules_factory.interfaces.ImportModulesFactoryInterface import ImportModulesFactoryInterface


class ImportModulesFactory(ImportModulesFactoryInterface):
    def __init__(self, ):
        self.__logger = logging.getLogger("LibByzaticCommon-import_modules_factory-logger")

    def fabricate(self, relative_name: str, root_package=False, relative_globals=None, level=0) -> ModuleType:
        try:
            """
            Importer can only import modules, functions can be looked up on the module. \n
    
            USAGE EXAMPLE 1: \n
            original: from foo.bar import baz \n
            __importer: baz = self.__importer('foo.bar.baz') \n
    
            USAGE EXAMPLE 2: \n
            original: import foo.bar.baz \n
            __importer: foo = self.__importer('foo.bar.baz', root_package=True) \n
    
            USAGE EXAMPLE 3: \n
            original: from .. import baz (level = number of dots) \n
            __importer: baz = self.__importer('baz', relative_globals=globals(), level=2)
    
            :param relative_name:
            :param root_package:
            :param relative_globals:
            :param level:
            :return: ModuleType or OperationIncompleteException
            """
            self.__logger.debug(f"Import module ->  "
                                f"module relative name: {relative_name}")
            self.__logger.debug(f"Import module ->  "
                                f"module root package: {root_package}")
            self.__logger.debug(f"Import module ->  "
                                f"module relative globals: {relative_globals}")
            self.__logger.debug(f"Import module ->  "
                                f"module level: {level}")
            module: ModuleType = __import__(name=relative_name,
                                            locals=None,
                                            globals=relative_globals,
                                            fromlist=[] if root_package else [None],
                                            level=level)
            return module
        except ImportError as ie:
            raise OperationIncompleteException(
                f"import_modules_factory import error: "
                f"relative_name={relative_name}; "
                f"root_package={root_package}; "
                f"relative_globals={relative_globals}; "
                f"level={level}; "
                f"ImportError.args={ie.args}; "
                f"ImportError.msg={ie.msg}; "
            )
        except Exception as e:
            raise OperationIncompleteException(e.args)
