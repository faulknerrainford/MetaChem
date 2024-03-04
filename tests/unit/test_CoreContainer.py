from unittest import TestCase
import networkx as nx
import pandas as pd
from metachem.CoreContainer import DataFrameEnvironment


class TestDataFrameEnvironment(TestCase):

    def test_add(self):
        graph = nx.DiGraph()
        data = DataFrameEnvironment(graph, ["id1", "id2", "obj1", "obj2", "Prods"])
        dict_list = [{"id1": 1, "id2": 2, "obj1": 'A', "obj2": 'B', "Prods": ((3, 'AB'))},
                     {"id1": 3, "id2": 1, "obj1": 'AB', "obj2": 'A', "Prods": ((3, 'AB'), (1, 'A'))},
                     {"id1": 3, "id2": 2, "obj1": 'AB', "obj2": 'B', "Prods": ((4, 'ABB'))},
                     {"id1": 3, "id2": 4, "obj1": 'AB', "obj2": 'ABB', "Prods": ((5, 'ABABB'))}]
        data.add(dict_list)
        self.assertFalse(data.DataFrame.empty, "The dataframe is still empty")
        self.assertEqual(data.DataFrame.shape[0], 4, "Incorrect number of rows")

    def test_read(self):
        graph = nx.DiGraph()
        data = DataFrameEnvironment(graph, ["id1", "id2", "obj1", "obj2", "Prods"])
        dict_list = [{"id1": 1, "id2": 2, "obj1": 'A', "obj2": 'B', "Prods": ((3, 'AB'))},
                     {"id1": 3, "id2": 1, "obj1": 'AB', "obj2": 'A', "Prods": ((3, 'AB'), (1, 'A'))},
                     {"id1": 3, "id2": 2, "obj1": 'AB', "obj2": 'B', "Prods": ((4, 'ABB'))},
                     {"id1": 3, "id2": 4, "obj1": 'AB', "obj2": 'ABB', "Prods": ((5, 'ABABB'))}]
        temp_df = pd.DataFrame(dict_list)
        data.DataFrame = pd.concat([data.DataFrame, temp_df], ignore_index=True)
        ret = data.read()
        self.assertIsInstance(ret, pd.DataFrame, "Returned dataframe")
        self.assertFalse(ret.empty, "The dataframe is still empty")
        self.assertEqual(ret.shape[0], 4, "Incorrect number of rows")

    def test_remove(self):
        graph = nx.DiGraph()
        data = DataFrameEnvironment(graph, ["id1", "id2", "obj1", "obj2", "Prods"])
        dict_list = [{"id1": 1, "id2": 2, "obj1": 'A', "obj2": 'B', "Prods": ((3, 'AB'))},
                     {"id1": 3, "id2": 1, "obj1": 'AB', "obj2": 'A', "Prods": ((3, 'AB'), (1, 'A'))},
                     {"id1": 3, "id2": 2, "obj1": 'AB', "obj2": 'B', "Prods": ((4, 'ABB'))},
                     {"id1": 3, "id2": 4, "obj1": 'AB', "obj2": 'ABB', "Prods": ((5, 'ABABB'))}]
        temp_df = pd.DataFrame(dict_list)
        data.DataFrame = pd.concat([data.DataFrame, temp_df], ignore_index=True)
        data.remove(dict_list[3])
        self.assertFalse(data.DataFrame.empty, "The dataframe is still empty")
        self.assertEqual(data.DataFrame.shape[0], 3, "Incorrect number of rows")

