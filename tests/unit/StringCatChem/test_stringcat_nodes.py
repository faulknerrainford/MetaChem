from unittest import TestCase
from metachem.CoreContainer import ListEnvironment, ListSample, NestedGridTank
from metachem.StringCatChem import stringcat_nodes
import networkx as nx

graph = nx.DiGraph()
# containers
TTanks = NestedGridTank(graph)
Vtime = ListEnvironment(graph)
Vtime.add(0)
TTank = stringcat_nodes.StringCatTank(graph)
Scomposite = ListSample(graph)
Vreactions = ListEnvironment(graph)
Vreactions.add(0)
TLoad = NestedGridTank(graph)  # Empty tank used as place holder as no input tank needed


class Test(TestCase):

    def test_string_cat_tank(self):
        # flattens list correctly
        TTank.add("AA")
        self.assertEqual(["AA"], TTank.read(), "single particle not added correctly to empty list")
        TTank.add([["AB", "AC"]])
        self.assertEqual(["AA", "AB", "AC"], TTank.read(), "List not flattened")
        # returns error if asked to remove particle not in list
        with self.assertRaises(ValueError, msg="Failed to raise error removing partical not in list"):
            TTank.remove("BC")
        TTank.remove("AB")
        self.assertEqual(["AA", "AC"], TTank.read(), "Failed to remove particle")
        # check in graph
        self.assertIn(TTank, graph.nodes, "TTank not added to nodes")

    def test_string_cat_load_sampler(self):
        TTanks = NestedGridTank(graph)
        Sload = stringcat_nodes.StringCatLoadSampler(graph, TLoad, TTanks, size=100, tanks=400)
        Sload.read()
        Sload.pull()
        Sload.check()
        Sload.process()
        Sload.push()
        # check ttank size correct
        self.assertEqual(400, len(TTanks.read()), "Incorrect number of tanks")
        self.assertEqual(100, len(TTanks.read()[0]), "Incorrect size of tanks")
        # check graph contains node
        self.assertIn(Sload, graph.nodes, "SLoad not added to nodes")
        # check graph connected to containers
        self.assertIn((TLoad, Sload), graph.edges, "Connection to TLoad not added to graph")
        self.assertIn((Sload, TTanks), graph.edges, "Connection to TTanks not added to graph")

    def test_string_cat_decomp_decision(self):
        Scomposite.add("ASDTKHHIOUH")
        Ddecomp = stringcat_nodes.StringCatDecompDecision(graph, 2, Scomposite)
        Ddecomp.read()
        self.assertEqual(Ddecomp.process(), 1, "Fails to decompose particle with double letter")
        Ddecomp.push()
        Scomposite.remove("ASDTKHHIOUH")
        Scomposite.add("SDGHIO")
        self.assertEqual(["SDGHIO"], Scomposite.read(), "Did not remove and add particles correctly")
        Ddecomp.read()
        self.assertEqual(Ddecomp.process(), 0, "Tried to decompose particle with no double letter")
        Ddecomp.push()
        Scomposite.remove("SDGHIO")

    def test_string_cat_concat_action(self):
        Aconcat = stringcat_nodes.StringCatConcatAction(graph, Scomposite, Scomposite)
        Scomposite.add(["BBA", "CC"])
        # check node and connections added to graph
        self.assertIn(Aconcat, graph.nodes, "Node not added to graph")
        self.assertIn((Aconcat, Scomposite), graph.edges, "Outgoing container edge not added to graph")
        self.assertIn((Scomposite, Aconcat), graph.edges, "Incoming container edge not added to graph")
        # Check pull
        Aconcat.read()
        Aconcat.pull()
        self.assertEqual(Aconcat.sample, ["BBA", "CC"], "Incorrect sample read")
        self.assertEqual(Scomposite.list, [], "Sample not emptied")
        # Check process
        Aconcat.process()
        self.assertIn(Aconcat.sample, ["BBACC", ["BBACC"]], "Incorrect join")
        # Check push
        Aconcat.push()
        self.assertEqual(Scomposite.list, ["BBACC"], "Incorrect push to sample")

    def test_sting_cat_split_action(self):
        Scomposite.add("ASDTKHHIOUH")
        Asplit = stringcat_nodes.StingCatSplitAction(graph, Scomposite, Scomposite)
        # check node and edges added to graph
        self.assertIn(Asplit, graph.nodes, "Node not added to graph")
        self.assertIn((Asplit, Scomposite), graph.edges, "Outgoing container edge not added to graph")
        self.assertIn((Scomposite, Asplit), graph.edges, "Incoming container edge not added to graph")
        # check pull
        Asplit.read()
        Asplit.pull()
        self.assertEqual(Asplit.sample, "ASDTKHHIOUH", "Incorrect sample read")
        self.assertEqual(Scomposite.list, [], "Sample not emptied")
        # check process
        Asplit.process()
        self.assertEqual(Asplit.sample, ["ASDTKH", "HIOUH"], "Incorrect split")
        # check push
        Asplit.push()
        self.assertEqual(Scomposite.list, ["ASDTKH", "HIOUH"], "Incorrect push")

    def test_string_cat_transfers_sampler(self):
        TTanks = NestedGridTank(graph)
        # Set up TTanks
        Sload = stringcat_nodes.StringCatLoadSampler(graph, TLoad, TTanks, size=100, tanks=400)
        Sload.read()
        Sload.pull()
        Sload.check()
        Sload.process()
        Sload.push()
        # Check node and edges added to graph
        Stransfers = stringcat_nodes.StringCatTransfersSampler(graph, TTanks, TTanks, gridrows=20, gridcols=20,
                                                               samplesize=1)
        self.assertIn(Stransfers, graph.nodes, "Node not added to graph")
        self.assertIn((Stransfers, TTanks), graph.edges, "Outgoing edge to container not added to graph")
        self.assertIn((TTanks, Stransfers), graph.edges, "Incoming edge to container not added to graph")
        # Check pull
        Stransfers.read()
        self.assertEqual(0, len(Stransfers.pairs), "Pairs list not empty")
        Stransfers.pull()
        self.assertEqual(99, len(TTanks.read()[Stransfers.pairs[0][0]]), "Removed sample incorrectly")
        self.assertEqual(99, len(TTanks.read()[Stransfers.pairs[0][1]]), "Removed sample incorrectly")
        # Check push
        Stransfers.push()
        self.assertEqual(100, len(TTanks.read()[Stransfers.pairs[0][0]]), "Removed sample incorrectly")
        self.assertEqual(100, len(TTanks.read()[Stransfers.pairs[0][1]]), "Removed sample incorrectly")

