#
#
#
import unittest

from python_byzatic_commons.flattener.list_flattener import ListFlattener
from python_byzatic_commons.flattener.test.data.data_file import SAMPLE_LIST_DATA, SAMPLE_LIST_FLATTEN


class TestFlattenList(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def __get_flattener(self):
        flattener: ListFlattener = ListFlattener()
        return flattener

    def test_list_flattener_scope_list(self):
        flattener: ListFlattener = self.__get_flattener()
        flatten_data = flattener.flatten(SAMPLE_LIST_DATA)
        reference_flatten_data: dict = SAMPLE_LIST_FLATTEN
        self.assertEqual(reference_flatten_data, flatten_data)

    def test_list_flattener_empty_list(self):
        flattener: ListFlattener = self.__get_flattener()
        flatten_data = flattener.flatten([])
        reference_flatten_data: dict = {}
        self.assertEqual(reference_flatten_data, flatten_data)


if __name__ == '__main__':
    unittest.main()
