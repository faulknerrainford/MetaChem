from unittest import TestCase
from metachem.RBNworld import RBN, WatsonSpike
import pickle


class TestRBN(TestCase):

    def test_create_rbn(self):
        # generate RBN
        rbn = RBN(12, 2, 1)
        # file = open("data/test_data_RBN.pickle", "wb")
        # pickle.dump(rbn, file)
        # file.close()
        # check correct size
        self.assertEqual(rbn.n, len(rbn.nodeArray), "Incorrect number of nodes in rbn")
        # check correct connections
        for node in rbn.nodeArray:
            self.assertEqual(rbn.k, len(node.connections), "Incorrect number of connections in node")
        # check generated spikes
        self.assertGreater(len(rbn.spikeArray), 0, "No spikes generated.")
        # check generated correct spike type, once more than one type.
        for spike in rbn.spikeArray:
            self.assertIsInstance(spike, WatsonSpike, "Incorrect spikes generated")

    def test_intensity_of_spikes(self):
        rbn = RBN(12, 2, 1)
        for spike in rbn.spikeArray:
            self.assertNotEqual(spike.intensity, 0, "Spike intensities not correctly set")

    def test_update_rbn(self):
        # Create rbn
        f = open("data/test_data_RBN.pickle", 'rb')
        rbn = pickle.load(f)
        f.close()
        # save initial state
        state = rbn.states
        numIt = rbn.numIterations
        # update
        rbn.updateRBN()
        # check it count went up
        self.assertEqual(rbn.numIterations, numIt+1, "Iteration count incorrect")
        # check state change
        self.assertFalse(self.assertListEqual(list(rbn.states[0]), list(state)), "State not updated")
        # check some states against bool functions
        self.assertListEqual([1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1], list(rbn.states[-1]), "Incorrect updated state")

    def test_reset_rbn(self):
        # Create rbn and record initial state
        f = open("data/test_data_RBN.pickle", 'rb')
        rbn = pickle.load(f)
        f.close()
        state = rbn.states
        numIt = rbn.numIterations
        # update rbn 5 times
        for _ in range(5):
            rbn.updateRBN()
        # check number of iterations correct
        self.assertEqual(rbn.numIterations, numIt+5, "Incorrect iteration count")
        # reset rbn
        rbn.resetRBN()
        # check clears iterations
        self.assertEqual(rbn.numIterations, 0, "Did not clear iteration count")
        # check clears state to initial state
        self.assertListEqual(list(state), list(rbn.states), "Did not reset state")

    def test_find_cycle_length(self):
        # load rbn for test
        f = open("data/test_data_RBN.pickle", 'rb')
        rbn = pickle.load(f)
        f.close()
        # run find_cycle length
        cl = rbn.findCycleLength()
        # check length correct with pre calc
        self.assertEqual(2, cl, "Incorrect cycle length")

    def test_zero_rbn(self):
        # set up rbn
        f = open("data/test_data_RBN.pickle", 'rb')
        rbn = pickle.load(f)
        f.close()
        # update a few times
        for _ in range(5):
            rbn.updateRBN()
        # record state and it count
        state = rbn.states
        numIt = rbn.numIterations
        # zero rbn
        rbn.zeroRBN()
        # check it count zero
        self.assertEqual(rbn.numIterations, 0, "Incorrect number of iterations")
        # check state unchanged
        self.assertEqual([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], list(rbn.states), "Incorrect state reset")
