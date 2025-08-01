#
#
#
import unittest

from python_byzatic_commons.flattener.dl_flattener import DLFlattener
from python_byzatic_commons.flattener.test.data.data_file import SAMPLE_DICT_DATA, SAMPLE_DICT_FLATTEN, \
    SAMPLE_LIST_DATA, SAMPLE_LIST_FLATTEN


class TestFlattenDL(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def __get_flattener(self):
        flattener: DLFlattener = DLFlattener()
        return flattener

    def test_dl_flattener_scope_dict(self):
        flattener: DLFlattener = self.__get_flattener()
        flatten_data = flattener.flatten(SAMPLE_DICT_DATA)
        reference_flatten_data: dict = SAMPLE_DICT_FLATTEN
        self.assertEqual(reference_flatten_data, flatten_data)

    def test_dl_flattener_empty_dict(self):
        flattener: DLFlattener = self.__get_flattener()
        flatten_data = flattener.flatten({})
        reference_flatten_data: dict = {}
        self.assertEqual(reference_flatten_data, flatten_data)

    def test_dl_flattener_scope_list(self):
        flattener: DLFlattener = self.__get_flattener()
        flatten_data = flattener.flatten(SAMPLE_LIST_DATA)
        reference_flatten_data: dict = SAMPLE_LIST_FLATTEN
        self.assertEqual(reference_flatten_data, flatten_data)

    def test_dl_flattener_empty_list(self):
        flattener: DLFlattener = self.__get_flattener()
        flatten_data = flattener.flatten([])
        reference_flatten_data: dict = {}
        self.assertEqual(reference_flatten_data, flatten_data)


if __name__ == '__main__':
    unittest.main()
