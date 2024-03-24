from unittest import TestCase

import networkx as nx

from metachem import CoreContainer, CoreControl


class TestClockObserver(TestCase):
    def test_read(self):
        graph = nx.DiGraph()
        VTime = CoreContainer.ListEnvironment(graph)
        VTime.add(0)
        otime = CoreControl.ClockObserver(graph, VTime, VTime)
        otime.read()
        self.assertEqual(otime.clock, 0, "Incorrect time read")

    def test_pull(self):
        graph = nx.DiGraph()
        VTime = CoreContainer.ListEnvironment(graph)
        VTime.add(0)
        otime = CoreControl.ClockObserver(graph, VTime, VTime)
        otime.clock = 0
        otime.pull()
        self.assertEqual(VTime.read(), [], "Time not removed from clock")

    def test_process(self):
        graph = nx.DiGraph()
        VTime = CoreContainer.ListEnvironment(graph)
        otime = CoreControl.ClockObserver(graph, VTime, VTime)
        otime.clock = 6
        otime.process()
        self.assertEqual(otime.clock, 7, "Clock did not increment")

    def test_push(self):
        graph = nx.DiGraph()
        VTime = CoreContainer.ListEnvironment(graph)
        otime = CoreControl.ClockObserver(graph, VTime, VTime)
        otime.clock = 6
        otime.push()
        self.assertEqual(VTime.read(), [6], "Clock did not push correctly")

    def test_transition(self):
        graph = nx.DiGraph()
        VTime = CoreContainer.ListEnvironment(graph)
        VTime.add(6)
        otime = CoreControl.ClockObserver(graph, VTime, VTime)
        otime.transition()
        self.assertEqual(VTime.read(), [7], "Clock did not push correctly")


class test_Simple_Sampler(TestCase):

    def test_read(self):
        graph = nx.DiGraph()
        TTank = CoreContainer.ListTank(graph)
        SSample = CoreContainer.ListSample(graph)
        ssampler = CoreControl.SimpleSampler(graph, SSample, TTank, size=2)
        TTank.list = [0, 1, 2, 3, 4]
        SSample.list = [5, 6, 7, 8, 9]
        ssampler.transition()
        self.assertEqual(7, len(TTank.list), "Incorrect sampling")
        ssampler.transition()
        self.assertEqual(9, len(TTank.list), "Incorrect sampling")
        ssampler.transition()
        self.assertEqual(1, len(SSample.list), "Incorrect sampling")
