from unittest import TestCase

import networkx as nx
import string
import random

from metachem import CoreControl, CoreContainer, Simulate
from metachem.StringCatChem import stringcat_nodes


class TestNestedGridTank(TestCase):

    def test_add_full(self):
        graph = nx.DiGraph()
        TTanks = CoreContainer.NestedGridTank(graph)
        sample = [[random.choice(string.ascii_uppercase) for _ in range(0, 100)] for _ in range(0, 400)]
        TTanks.add(sample, full=True)
        self.assertEqual(400, len(TTanks.dict.keys()), "Incorrect number of tanks stored")
        self.assertEqual(100, len(TTanks.dict[0]), "Incorrect sized tanks created")

    def test_remove_tank(self):
        graph = nx.DiGraph()
        TTanks = CoreContainer.NestedGridTank(graph)
        sample = [[random.choice(string.ascii_uppercase) for _ in range(0, 100)] for _ in range(0, 400)]
        TTanks.add(sample, full=True)
        sample = random.sample(list(TTanks.read().values()), min(1, len(list(TTanks.read().values()))))
        [TTanks.remove(elem) for elem in sample]
        self.assertNotIn(sample, TTanks.dict.values(), "Sampled tank not removed")

    def test_remove_particle(self):
        self.fail()

    def test_add_tank(self):
        graph = nx.DiGraph()
        TTanks = CoreContainer.NestedGridTank(graph)
        sample = [[random.choice(string.ascii_uppercase) for _ in range(0, 100)] for _ in range(0, 400)]
        TTanks.add(sample, full=True)
        sample = random.sample(list(TTanks.read().values()), min(1, len(list(TTanks.read().values()))))
        [TTanks.remove(elem) for elem in sample]
        sample = sample[0]
        keys = TTanks.dict.keys()
        for key in keys:
            if not TTanks.dict[key]:
                TTanks.add(sample, tank=key)
                break
        for tank in TTanks.dict.values():
            self.assertEqual(100, len(tank), "Tank with incorrect length")

    def test_add_particle(self):
        self.fail()
