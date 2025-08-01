#!/usr/bin/env python3
#
# ========= Interfaces ========= 
#
#
#
#
import logging
from logging import Logger
import inspect
from copy import deepcopy
from python_byzatic_commons.in_memory_storages.interfaces import KeyValueListStorageInterface
from python_byzatic_commons.exceptions import OperationIncompleteException


class KeyValueListStorage(KeyValueListStorageInterface):
    def __init__(self, storage_name: str, critical_dump_flag: bool = True):
        """
        KeyValueStringStorage is an In memory storage based on KeyValueCRUDInterface
        LibByzaticCommon.crud.interfaces.KeyValueCRUDInterface
        Is a descendant of the LibByzaticCommon.NodeStorage.interfaces.KeyValueStringStorageInterface
        Brief description of application:
                                        Key: str
                                        Value: list
        @param storage_name: name of the current storage displayed in the log entry
        @param critical_dump_flag: Bool flag to display full storage in the log entry
        """
        self.__logger: Logger = logging.getLogger("LibByzaticCommon-NodeStorage-logger")
        self.__storage: dict = {}
        self.__storage_name: str = storage_name
        self.__critical_dump_flag = critical_dump_flag

    def create(self, key: str, value: list) -> None:
        """
        Create string value in storage by key
        @param key: string identification parameter
        @param value: string value parameter
        @return: None if success or raise OperationIncompleteException
        """
        try:
            ops_name = str(inspect.currentframe().f_code.co_name)
            self.__logger.debug(f"storage: {self.__storage_name} "
                                f"operation: {ops_name} "
                                f"msg: Create key -> {key} value -> {value}")
            self.__check_if_value_empty(value, ops_name)
            self.__check_if_key_empty(key, ops_name)
            if key not in self.__storage:
                self.__storage[key] = self.__local_deepcopy(value, ops_name)
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: The value was successfully added to the storage by key")
            else:
                self.__critical_dump()
                raise OperationIncompleteException(f"storage: {self.__storage_name} "
                                                   f"operation: {ops_name} "
                                                   f"msg: Key {key} already exists in storage")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def read(self, key: str) -> list:
        """
        Read string value in storage by key
        @param key: string identification parameter
        @return: str if success or raise OperationIncompleteException
        """
        try:
            ops_name = str(inspect.currentframe().f_code.co_name)
            self.__logger.debug(f"storage: {self.__storage_name} "
                                f"operation: {ops_name} "
                                f"msg: Read value by key {key}")
            self.__check_if_key_empty(key, ops_name)
            if key in self.__storage:
                object_rq = self.__storage[key]
                deep_value = self.__local_deepcopy(object_rq, ops_name)
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: Value with key {key} was read successfully: {str(object_rq)}")
                return deep_value
            else:
                self.__critical_dump()
                raise OperationIncompleteException(f"storage: {self.__storage_name} "
                                                   f"operation: {ops_name} "
                                                   f"msg: Can't get value by key {key} because no such key in storage")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def update(self, key: str, value: list) -> int:
        """
        Update string value in storage by key
        @param key: string identification parameter
        @param value: string value parameter
        @return: 0 if success or raise OperationIncompleteException
        """
        try:
            ops_name = str(inspect.currentframe().f_code.co_name)
            deep_value = self.__local_deepcopy(value, ops_name)
            self.__logger.debug(f"storage: {self.__storage_name} "
                                f"operation: {ops_name} "
                                f"msg: Update value by key {key} with value {deep_value}")
            self.__check_if_key_empty(key, ops_name)
            self.__check_if_value_empty(value, deep_value)
            if key in self.__storage:
                previous_value: dict = self.__storage[key]
                self.__storage[key] = deep_value
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: Value {previous_value} was successfully updated by key {key} "
                                    f"with value {self.__storage[key]}")
                return 0
            else:
                self.__critical_dump()
                raise OperationIncompleteException(f"storage: {self.__storage_name} "
                                                   f"operation: {ops_name} "
                                                   f"msg: Value by key {key}"
                                                   f" couldn't be updated because key doesn't exists")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def delete(self, key: str) -> int:
        """
        Delete string value in storage by key
        @param key: string identification parameter
        @return: 0 if success or raise OperationIncompleteException
        """
        try:
            ops_name = str(inspect.currentframe().f_code.co_name)
            self.__logger.debug(f"storage: {self.__storage_name} "
                                f"operation: {ops_name} "
                                f"msg: Delete value and key by key {key}")
            self.__check_if_key_empty(key, ops_name)
            if key in self.__storage:
                del self.__storage[key]
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: Value with key {key} was successfully removed")
                return 0
            else:
                self.__critical_dump()
                raise OperationIncompleteException(f"storage: {self.__storage_name} "
                                                   f"operation: {ops_name} "
                                                   f"msg: Can't remove value with key {key} because storage "
                                                   f"doesn't contains such key")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def drop(self) -> int:
        """
        Drop all value and keys in storage
        @return: 0 if success or raise OperationIncompleteException
        """
        try:
            ops_name = str(inspect.currentframe().f_code.co_name)
            self.__storage = {}
            self.__logger.debug(f"storage: {self.__storage_name} "
                                f"operation: {ops_name} "
                                f"msg: Storage was successfully pruned: {str(self.__storage)}")
            return 0
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def read_all(self) -> dict:
        """
        Read all value and keys in storage
        @return: dict if success or raise OperationIncompleteException
        """
        try:
            ops_name = str(inspect.currentframe().f_code.co_name)
            storage_object = self.__local_deepcopy(self.__storage, ops_name)
            self.__logger.debug(f"storage: {self.__storage_name} "
                                f"operation: {ops_name} "
                                f"msg: Full storage was read successfully: {str(storage_object)}")
            return storage_object
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def read_list_keys(self) -> list:
        """
        Read list of all keys in storage
        @return: list if success or raise OperationIncompleteException
        """
        try:
            ops_name = str(inspect.currentframe().f_code.co_name)
            list_items: list = []
            for i, v in self.__storage.items():
                list_items.append(i)
            self.__logger.debug(f"storage: {self.__storage_name} "
                                f"operation: {ops_name} "
                                f"msg: Full list of key was read: {str(list_items)}")
            return list_items
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def contains(self, key: str) -> bool:
        """
        Check if key contains in storage
        @return: bool if success or raise OperationIncompleteException
        """
        try:
            ops_name = str(inspect.currentframe().f_code.co_name)
            if key in self.__storage:
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: Key {key} exists in storage")
                return True
            else:
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: Key {key} doesn't exists in storage")
                return False
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def __critical_dump(self) -> None:
        try:
            ops_name = str(inspect.currentframe().f_code.co_name)
            if self.__critical_dump_flag:
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: storage critical dump -> {self.__storage}")
            else:
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: storage critical dump disabled")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def __local_deepcopy(self, value, ops_name):
        try:
            self.__logger.debug(f"storage: {self.__storage_name} "
                                f"operation: {ops_name} "
                                f"msg: Running deepcopy for {value}")
            deepcopy_value = deepcopy(value)
            self.__logger.debug(f"storage: {self.__storage_name} "
                                f"operation: {ops_name} "
                                f"msg: Deepcopy successfully finished")
            return deepcopy_value
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def __check_if_value_empty(self, value: list, ops_name: list) -> None:
        try:
            if value == []:
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: value str is empty")
            elif value is None:
                self.__logger.debug(f"storage: {self.__storage_name} "
                                    f"operation: {ops_name} "
                                    f"msg: value is None")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def __check_if_key_empty(self, key: str, ops_name: str) -> None:
        try:
            if len(key) == 0:
                self.__logger.critical(f"length of key is 0")
                raise OperationIncompleteException(f"storage: {self.__storage_name}"
                                                   f"operation: {ops_name} "
                                                   f"msg: key: {key} is 0")
            elif key == "":
                self.__logger.critical(f"length of key is empty")
                raise OperationIncompleteException(f"storage: {self.__storage_name}"
                                                   f"operation: {ops_name} "
                                                   f"msg: key: {key} is empty")
            elif key is None:
                self.__logger.critical(f"key is None")
                raise OperationIncompleteException(f"storage: {self.__storage_name}"
                                                   f"operation: {ops_name} "
                                                   f"msg: key: {key} is None")
        except OperationIncompleteException as oie:
            raise OperationIncompleteException(oie.args, errno=oie.errno)
        except Exception as err:
            raise OperationIncompleteException(err.args)
