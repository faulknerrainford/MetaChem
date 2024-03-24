from unittest import TestCase
import pickle

import networkx as nx

from metachem import CoreContainer as cc
from metachem.RBNworld.RBNSpikeyWatsonBond import SpikeDecision, WatsonSpikeBond, SpikeStabilityObservation, \
    SpikeBondBreak


class TestRBNSpikeyWatsonBond(TestCase):

    pass


class TestSpikeDecision(TestCase):

    def test_SpikeDecision(self):
        file = open("data/test_data_RBNparticles.pickle", "rb")
        particles = pickle.load(file)
        file.close()
        graph = nx.DiGraph()
        sample = cc.ListSample(graph)
        sample.add(particles[15])
        sample.add(particles[17])
        dec = SpikeDecision(graph, sample)
        self.assertEqual(0, dec.transition(), "Did not find bonding potential")
        sample.remove(particles[15])
        sample.add(particles[18])
        self.assertEqual(1, dec.transition(), "Incorrect bonding attempt")


class TestWatsonSpikeBond(TestCase):

    def test_WatsonSpikeBond(self):
        file = open("data/test_data_RBNparticles.pickle", "rb")
        particles = pickle.load(file)
        file.close()
        graph = nx.DiGraph()
        sample = cc.ListSample(graph)
        sample.add(particles[15])
        sample.add(particles[20])
        act = WatsonSpikeBond(graph, sample, sample)
        act.transition()
        # file = open("data/test_RBN_bonded_particle.pickle", "wb")
        # pickle.dump(sample.read(), file)
        # file.close()
        file = open("data/test_RBN_bonded_particle.pickle", "rb")
        bonded_part = pickle.load(file)[0]
        file.close()
        self.assertEqual(1, len(sample.read()), "Did not bond and return particle")
        self.assertListEqual([atom.rbnNumber for atom in bonded_part.atoms],
                             [atom.rbnNumber for atom in sample.read()[0].atoms], "Incorrect particle")
        self.assertEqual(2, len(sample.read()[0].open_spikes), "Incorrect number of open spikes")


class TestSpikeStabilityObservation(TestCase):

    def test_SpikeStabilityObservation(self):
        file = open("data/test_RBN_bonded_particle.pickle", "rb")
        bonded_part = pickle.load(file)
        file.close()
        graph = nx.DiGraph()
        sample = cc.ListSample(graph)
        env = cc.ListEnvironment(graph)
        env.add("Nonsense")
        sample.add(bonded_part)
        obs = SpikeStabilityObservation(graph, env, env, sample)
        obs.transition()
        self.assertNotIn("Nonsense", env.read(), "Did not clear environment")
        self.assertEqual(1, len(env.read()), "Did not find broken bond")
        # TODO: save out state after obersevation of this and the sample to test the bond break
        # TODO: Find cause of nested list in broken bonds
        # TODO: Find where sample emptied


class TestSpikeBondBreak(TestCase):

    def test_SpikeBondBreak(self):
        file = open("data/test_RBN_bonded_particle.pickle", "rb")
        bonded_part = pickle.load(file)
        file.close()
        graph = nx.DiGraph()
        sample = cc.ListSample(graph)
        env = cc.ListEnvironment(graph)
        sample.add(bonded_part)
        obs = SpikeStabilityObservation(graph, env, env, sample)
        obs.transition()
        bact = SpikeBondBreak(graph, sample, sample, env)
        bact.transition()
        self.assertEqual(2, len(sample.read()), "Bond not broken")
        self.assertEqual(18, sample.read()[0].atoms[0].rbnNumber, "Incorrect first particle after break")
        self.assertEqual(23, sample.read()[1].atoms[0].rbnNumber, "Incorrect second particle after break")
