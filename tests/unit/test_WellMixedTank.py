from unittest import TestCase

import networkx as nx

from metachem.templates.WellMixedTank import LoadSampler, TimingsDecision, WellMixedTank
from metachem import CoreContainer, CoreNode
from metachem.RBNworld import RBNSpikeyWatsonBond, WatsonRBNParticleFactory
from metachem import Simulate


class TestWellMixedTank(TestCase):
    def test_run(self):
        self.fail()

    def test_rbn_run(self):
        bond = RBNSpikeyWatsonBond()
        tank = WellMixedTank(bond, sample_size=2, load_type='RBN', generations=100)
        # tank.print_tank()
        sim = Simulate(tank.graph, tank.start, verbose=False)
        sim.run_graph(1000000000)
        tank.print_tank()


class TestLoadSampler(TestCase):

    def test_read(self):
        graph = nx.DiGraph()
        TTank = CoreContainer.ListTank(graph)
        sload = LoadSampler(graph, TTank, load_type="csv", load_file="/home/psmr500/PycharmProjects/MetaChem/tests/unit"
                                                                     "/test_load_data.csv")
        sload.read()
        self.assertEqual(1000, len(sload.sample), "Full csv not loaded in read stage")

    def test_pull(self):
        graph = nx.DiGraph()
        TTank = CoreContainer.ListTank(graph)
        sload = LoadSampler(graph, TTank, tank_size=1000, load_type="scc")
        sload.pull()
        self.assertEqual(1000, len(sload.sample), "Did not generate full tank of scc particles")
        sload = LoadSampler(graph, TTank, tank_size=1000, load_type="int")
        sload.pull()
        self.assertEqual(1000, len(sload.sample), "Did not generate full tank of int particles")

    def test_push(self):
        graph = nx.DiGraph()
        TTank = CoreContainer.ListTank(graph)
        sload = LoadSampler(graph, TTank, tank_size=1000, load_type="scc")
        sload.pull()
        self.assertEqual(1000, len(sload.sample), "Did not generate full tank of scc particles")
        sload = LoadSampler(graph, TTank, tank_size=1000, load_type="int")
        sload.pull()
        sload.push()
        self.assertEqual(1000, len(TTank.list), "Did not push to tank correctly")

    def test_rbn(self):
        graph = nx.DiGraph()
        TTank = CoreContainer.ListTank(graph)
        sload = LoadSampler(graph, TTank, tank_size=1000, load_type="RBN")
        sload.read()
        sload.pull()
        self.assertEqual(1000, len(sload.sample), "Did not generate full tank of rbn particles")


class TestTimingsDecision(TestCase):

    def test_read(self):
        graph = nx.DiGraph()
        Vtime = CoreContainer.ListEnvironment(graph)
        Vtime.add(17)
        VGen = CoreContainer.ListEnvironment(graph)
        VGen.add(83)
        dloop = TimingsDecision(graph, [VGen, Vtime], 1000, 1000)
        dloop.read()
        self.assertEqual(dloop.time, 17, "Time incorrect")
        self.assertEqual(dloop.gen, 83, "Gen incorrect")

    def test_process(self):
        graph = nx.DiGraph()
        dloop = TimingsDecision(graph, None, 1000, 1000)
        dloop.time = 17
        dloop.gen = 83
        self.assertEqual(0, dloop.process(), "Failed to loop on bonding within gen.")
        dloop.gen = 1000
        self.assertEqual(1, dloop.process(), "Failed to loop at end of generation")
        dloop.gen = 83
        dloop.time = 1000
        self.assertEqual(0, dloop.process(), "Failed to complete final generation")
        dloop.gen = 1000
        self.assertEqual(2, dloop.process(), "Failed to terminate")
