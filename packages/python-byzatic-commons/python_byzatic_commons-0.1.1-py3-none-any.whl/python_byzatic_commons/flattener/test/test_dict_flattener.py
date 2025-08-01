#
#
#
import unittest

from python_byzatic_commons.flattener.dictionary_flattener import DictionaryFlattener
from python_byzatic_commons.flattener.test.data.data_file import SAMPLE_DICT_DATA, SAMPLE_DICT_FLATTEN


class TestFlattenDict(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def __get_flattener(self):
        flattener: DictionaryFlattener = DictionaryFlattener()
        return flattener

    def test_dict_flattener_scope_dict(self):
        flattener: DictionaryFlattener = self.__get_flattener()
        flatten_data = flattener.flatten(SAMPLE_DICT_DATA)
        reference_flatten_data: dict = SAMPLE_DICT_FLATTEN
        self.assertEqual(reference_flatten_data, flatten_data)

    def test_dict_flattener_empty_dict(self):
        flattener: DictionaryFlattener = self.__get_flattener()
        flatten_data = flattener.flatten({})
        reference_flatten_data: dict = {}
        self.assertEqual(reference_flatten_data, flatten_data)


if __name__ == '__main__':
    unittest.main()
