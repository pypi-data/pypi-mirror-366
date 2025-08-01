#
#
#
import logging

from python_byzatic_commons.exceptions import OperationIncompleteException

from python_byzatic_commons.in_memory_storages.interfaces import KeyValueObjectStorageInterface
from python_byzatic_commons.in_memory_storages.interfaces import KeyValueStoragesStorageInterface
from python_byzatic_commons.in_memory_storages.interfaces import KeyValueDictStorageInterface
from python_byzatic_commons.in_memory_storages.interfaces import KeyValueStorageInterface
from python_byzatic_commons.in_memory_storages.interfaces import KeyValueStringStorageInterface

from python_byzatic_commons.in_memory_storages.key_value_storages import KeyValueDictStorage
from python_byzatic_commons.in_memory_storages.key_value_storages import KeyValueObjectStorage
from python_byzatic_commons.in_memory_storages.key_value_storages import KeyValueStoragesStorage
from python_byzatic_commons.in_memory_storages.key_value_storages import KeyValueStringStorage

from python_byzatic_commons.singleton.Singleton import Singleton


class StoragesManager(Singleton):
    def __init__(self):
        self.__logger: logging.Logger = logging.getLogger("basic_logger")
        self.__storage: KeyValueStorageInterface = KeyValueStoragesStorage("StorageManager_storage", True)

    def get(self, storage_type: KeyValueStorageInterface, storage_name: str, critical_dump_flag: bool = True) -> KeyValueStorageInterface:
        """
        Native Byzatic storage manager
        @param storage_type: instance of KeyValueStorageInterface
        (look at LibByzaticCommon.NodeStorage.interfaces.Readers)
        @param storage_name: name of storage
        @param critical_dump_flag: True by default or False
        @return: instance of KeyValueStorageInterface
        """
        try:
            storage: KeyValueStorageInterface
            if isinstance(storage_type, KeyValueDictStorageInterface):
                return self.__keyvaluedictstorage_init(storage_name, critical_dump_flag)
            elif isinstance(storage_type, KeyValueObjectStorageInterface):
                return self.__keyvalueobjectstorage_init(storage_name, critical_dump_flag)
            elif isinstance(storage_type, KeyValueStoragesStorageInterface):
                return self.__keyvaluestringstorage_init(storage_name, critical_dump_flag)
            else:
                raise OperationIncompleteException(f"StoragesManager: requested storage type is not an "
                                                   f"instance of AbstractKeyValueStorage")
        except Exception as err:
            raise OperationIncompleteException(err.args)

    def __keyvaluedictstorage_init(self, storage_name: str, critical_dump_flag: bool = True):
        storage: KeyValueStorageInterface
        if self.__storage.contains(storage_name):
            storage = self.__storage.read(storage_name)
            if isinstance(storage, KeyValueDictStorageInterface):
                pass
            else:
                raise OperationIncompleteException(f"StoragesManager: requested storage is not a "
                                                   f"type of AbstractKeyValueDictStorage")
            self.__logger.debug(f"Storage with name {storage_name} already exists, return {storage_name}")
        else:
            storage = KeyValueDictStorage(storage_name, critical_dump_flag)
            self.__storage.create(storage_name, storage)
            self.__logger.debug(f"Created instance of AbstractKeyValueDictStorage storage: {storage_name}")
        return storage

    def __keyvalueobjectstorage_init(self, storage_name: str, critical_dump_flag: bool = True):
        storage: KeyValueStorageInterface
        if self.__storage.contains(storage_name):
            storage = self.__storage.read(storage_name)
            if isinstance(storage, KeyValueObjectStorageInterface):
                pass
            else:
                raise OperationIncompleteException(f"StoragesManager: requested storage is not a "
                                                   f"type of AbstractKeyValueObjectStorage")
            self.__logger.debug(f"Storage with name {storage_name} already exists, return {storage_name}")
        else:
            storage = KeyValueObjectStorage(storage_name, critical_dump_flag)
            self.__storage.create(storage_name, storage)
            self.__logger.debug(f"Created instance of AbstractKeyValueDictStorage storage: {storage_name}")
        return storage

    def __keyvaluestringstorage_init(self, storage_name: str, critical_dump_flag: bool = True):
        storage: KeyValueStringStorageInterface
        if self.__storage.contains(storage_name):
            storage = self.__storage.read(storage_name)
            if isinstance(storage, KeyValueStringStorageInterface):
                pass
            else:
                raise OperationIncompleteException(f"StoragesManager: requested storage is not a "
                                                   f"type of AbstractKeyValueObjectStorage")
            self.__logger.debug(f"Storage with name {storage_name} already exists, return {storage_name}")
        else:
            storage = KeyValueStringStorage(storage_name, critical_dump_flag)
            self.__storage.create(storage_name, storage)
            self.__logger.debug(f"Created instance of AbstractKeyValueDictStorage storage: {storage_name}")
        return storage
