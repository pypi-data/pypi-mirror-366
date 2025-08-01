#
#
#
import unittest
from python_byzatic_commons.in_memory_storages.key_value_storages import KeyValueDictStorage
from python_byzatic_commons.exceptions import OperationIncompleteException
from python_byzatic_commons.in_memory_storages.interfaces import KeyValueDictStorageInterface


class TestKeyValueDictStorage(unittest.TestCase):
    def setUp(self):
        self.__empty_data = {}
        self.__data = {
            "foo": 1,
            "bar": "foo"
        }

    def tearDown(self):
        pass

    def __get_storage(self):
        storage_name: str = "key_value_dict_storage"
        key_value_dict_storage: KeyValueDictStorageInterface = KeyValueDictStorage(storage_name)
        return key_value_dict_storage

    def test_storage_create(self):
        storage: KeyValueDictStorageInterface = self.__get_storage()
        storage.create("foo", self.__data)
        data = storage.read("foo")
        self.assertEqual(self.__data, data)

    def test_storage_read(self):
        storage: KeyValueDictStorageInterface = self.__get_storage()
        storage.create("foo", self.__data)
        data = storage.read("foo")
        self.assertEqual(self.__data, data)

    def test_storage_update(self):
        storage: KeyValueDictStorageInterface = self.__get_storage()
        storage.create("foo", self.__data)
        entry_data: dict = {"bar": 1}
        storage.update("foo", entry_data)
        data = storage.read("foo")
        self.assertEqual(entry_data, data)

    def test_storage_delete(self):
        try:
            storage: KeyValueDictStorageInterface = self.__get_storage()
            storage.create("foo", self.__data)
            storage.delete("foo")
            storage.read("foo")
        except Exception as err:
            self.assertIsInstance(err, OperationIncompleteException)

    def test_storage_drop(self):
        try:
            storage: KeyValueDictStorageInterface = self.__get_storage()
            storage.create("foo", self.__data)
            storage.drop()
            storage.read("foo")
        except Exception as err:
            self.assertIsInstance(err, OperationIncompleteException)

    def test_storage_read_all(self):
        storage: KeyValueDictStorageInterface = self.__get_storage()
        entry_data = {
            "foo": self.__data
        }
        storage.create("foo", self.__data)
        data = storage.read_all()
        self.assertEqual(entry_data, data)

    def test_storage_read_list_keys(self):
        storage: KeyValueDictStorageInterface = self.__get_storage()
        storage.create("foo", self.__data)
        data = storage.read_list_keys()
        self.assertEqual("foo", data[0])

    def test_storage_contains(self):
        storage: KeyValueDictStorageInterface = self.__get_storage()
        storage.create("foo", self.__data)
        data = storage.contains("foo")
        self.assertEqual(data, True)


if __name__ == '__main__':
    unittest.main()
