from metachem import Subgraph, CoreNode, CoreContainer
from metachem.RBNworld import RBNParticle
import numpy as np


class RBNSpikeyWatsonBond(Subgraph):

    def __init__(self, controls_in=1, controls_out=1, links=1):
        super(RBNSpikeyWatsonBond, self).__init__(controls_in, controls_out, links)

        # create envo container and link sample
        bb_container = CoreContainer.ListEnvironment(self.graph)
        link_sample = CoreContainer.LinkSample(self.graph)

        # create nodes
        spikes_check = SpikeDecision(self.graph, link_sample)
        bonding_spikes = WatsonSpikeBond(self.graph, link_sample, link_sample)
        stability = SpikeStabilityObservation(self.graph, bb_container, bb_container, link_sample)
        break_check = SpikeDecision(self.graph, bb_container)
        bond_break = SpikeBondBreak(self.graph, link_sample, link_sample, bb_container)

        # add dummy action node which does nothing to act as join for decisions
        null_sample = CoreNode.Sample(self.graph)
        null_act = CoreNode.Action(self.graph, null_sample, null_sample)

        # link up subgraph nodes
        self.graph.add_edge(spikes_check, bonding_spikes)
        self.graph.add_edge(spikes_check, null_act)
        self.graph.add_edge(bonding_spikes, stability)
        self.graph.add_edge(stability, break_check)
        self.graph.add_edge(break_check, null_act)
        self.graph.add_edge(break_check, bond_break)
        self.graph.add_edge(bond_break, stability)

        # set subgraph values
        self.links = [link_sample]
        self.control_in = [spikes_check]
        self.control_out = [null_act]


class SpikeDecision(CoreNode.Decision):

    def __init__(self, graph, readcontainers):
        super(SpikeDecision, self).__init__(graph, 2, readcontainers)
        self.particle1 = None
        self.particle2 = None

    def read(self):
        self.particle1, self.particle2 = self.readcontainers.read()

    def process(self):
        # TODO: add size considerations
        for spike1 in self.particle1.open_spikes:
            for spike2 in self.particle2.open_spikes:
                if spike1[0].intensity + spike2[0].intensity == 0:
                    return 0
        return 1


class WatsonSpikeBond(CoreNode.Action):

    def __init__(self, graph, readsample, writesample):
        super(WatsonSpikeBond, self).__init__(graph, readsample, writesample)
        self.rbn2 = None
        self.rbn1 = None
        self.particle1 = None
        self.particle2 = None
        self.new_particle = None
        self.spike1 = None
        self.spike2 = None

    def read(self):
        self.particle1, self.particle2 = self.readsample.read()

    def pull(self):
        self.readsample.remove(self.particle1)
        self.readsample.remove(self.particle2)

    def check(self):
        return super(WatsonSpikeBond, self).check()

    def process(self):
        for spike1 in self.particle1.open_spikes:
            for spike2 in self.particle2.open_spikes:
                if not spike1[0].intensity+spike2[0].intensity:
                    self.spike1 = spike1[0]
                    self.spike2 = spike2[0]
                    self.rbn1 = spike1[1]
                    self.rbn2 = spike2[1]
        self.spike1.hasBonded(self.particle2, self.spike2.spikeNumber)
        self.spike2.hasBonded(self.particle1, self.spike1.spikeNumber)
        smaller, size = findSmallestSpike(self.spike1, self.spike2)
        numSwaps = size - 1
        swapLinks(self.spike1, self.spike2, numSwaps, smaller)
        self.particle1.open_spikes.remove((self.spike1, self.rbn1))
        self.particle2.open_spikes.remove((self.spike2, self.rbn2))
        open_spikes = self.particle1.open_spikes + self.particle2.open_spikes
        bonds = [(self.spike1, self.rbn1, self.spike2, self.rbn2)] + self.particle1.bonds + self.particle2.bonds
        rbns = self.particle1.atoms + self.particle2.atoms
        self.new_particle = RBNParticle(rbns, bonds, open_spikes, "Watson")

    def push(self):
        if self.new_particle:
            self.writesample.add(self.new_particle)
        else:
            self.writesample.add(self.particle1)
            self.writesample.add(self.particle2)


class SpikeStabilityObservation(CoreNode.Observer):

    def __init__(self, graph, containersin, containersout, readcontainers):
        super(SpikeStabilityObservation, self).__init__(graph, containersin, containersout, readcontainers)
        self.particles = []
        self.broken_bonds = []

    def read(self):
        self.particles = self.readcontainers.read()

    def pull(self):
        self.containersin.remove(self.containersin.read())

    def check(self):
        return super(SpikeStabilityObservation, self).check()

    def process(self):
        for part in self.particles:
            if part.checkSpikes():
                self.broken_bonds.append((part, part.checkSpikes()))

    def push(self):
        self.containersout.add(self.broken_bonds)


class SpikeBondBreak(CoreNode.Action):

    def __init__(self, graph, readsample, writesample, readcontainers):
        super(SpikeBondBreak, self).__init__(graph, readsample, writesample, readcontainers)
        self.broken_bonds = None
        self.particles = []

    def read(self):
        self.broken_bonds = self.readcontainers.read()

    def pull(self):
        for bond in self.broken_bonds:
            part = bond[0]
            self.readsample.remove(part)

    def check(self):
        return super(SpikeBondBreak, self).check()

    def process(self):
        for bond in self.broken_bonds:
            part = bond[0]
            # TODO: find rbn1 and rbn2 put together spike rbn pairs for breaking bond
            broken = (bond[1])
            self.particles = self.particles + part.breakBond(broken)

    def push(self):
        self.writesample.add(self.particles)


class SpikeStabilityDecision(CoreNode.Decision):

    def __init__(self, graph, readcontainers):
        super(SpikeStabilityDecision, self).__init__(graph, 2, readcontainers)
        self.broken_bonds = []

    def read(self):
        self.broken_bonds = self.readcontainers.read()

    def process(self):
        if self.broken_bonds:
            return 1
        else:
            return 0


def findSmallestSpike(spike1, spike2):
    """ This function is used to determine which spike is the smallest
        and returns the smallest spike and its size
    """
    sizeSpike1 = np.size(spike1.returnNodeArray())
    # spike1.printNodeArray()
    sizeSpike2 = np.size(spike2.returnNodeArray())
    # spike2.printNodeArray()
    # print ("The size of spike 1 is: " + str(sizeSpike1) + "\n")
    # print("The size of spike 2 is: " + str(sizeSpike2) + "\n")
    if (sizeSpike1 <= sizeSpike2):
        return 1, sizeSpike1
    else:
        return 2, sizeSpike2


def swapLinks(spike1, spike2, numSwaps, smallestSpike):
    spike1NodeArray = spike1.returnNodeArray()
    spike2NodeArray = spike2.returnNodeArray()
    # Store the sizes of spikes, need to use original values later but also need temps ones
    refMaxS1Index = np.size(spike1NodeArray) - 1
    refMaxS2Index = np.size(spike2NodeArray) - 1
    maxS1Index = refMaxS1Index
    maxS2Index = refMaxS2Index

    if smallestSpike == 1:
        # print ("If statement called \n")
        spike2.addDanglingBonds(np.size(spike2.nodeList) - np.size(spike1.nodeList))
        for i in range(numSwaps):
            spike2NodeArray[maxS2Index - 1].involvedInBond(spike2NodeArray[maxS2Index], spike1NodeArray[maxS1Index])
            spike1NodeArray[maxS1Index - 1].involvedInBond(spike1NodeArray[maxS1Index], spike2NodeArray[maxS2Index])

            maxS1Index = maxS1Index - 1
            maxS2Index = maxS2Index - 1

    else:
        # print ("Else statement called \n")
        spike1.addDanglingBonds(np.size(spike1.nodeList) - np.size(spike2.nodeList))
        for i in range(numSwaps):
            spike1NodeArray[maxS1Index - 1].involvedInBond(spike1NodeArray[maxS1Index], spike2NodeArray[maxS2Index])
            spike2NodeArray[maxS2Index - 1].involvedInBond(spike2NodeArray[maxS2Index], spike1NodeArray[maxS1Index])

            maxS1Index = maxS1Index - 1
            maxS2Index = maxS2Index - 1

    spike1.changeNodeArray(spike1NodeArray)
    spike2.changeNodeArray(spike2NodeArray)


def calculateIntensitySpikes(self, mol):
    """ This function calculates the intensity of every spike in the molecule, it does this by updating the molecule
        and then calculating the intensity of evey spike
    """

    origStates = []
    for i in range(len(mol)):
        origStates.append(mol[i].states)
        mol[i].zeroRBN()

        # print ("The state matrix for atom " + str(i) + " is: \n" + str(mol[i].states) + "\n")
    for i in range(self.maxSizeAtom + 30):
        self.updateMolecule(mol)

    self.analyseMolecule(mol)

    for i in range(len(mol)):
        mol[i].setState(origStates[i], np.size(origStates[i], 0) - 1)