import string
import random
from metachem import CoreControl, CoreContainer, CoreNode


# List of needed control nodes.rst:
#   s:load - input set of strings
#   o:time - increments time between generations - (ClockObserver)
#   s:samplertank - Chooses a tank to work over that hasn't been chosen in the current generation - (SimpleSampler)
#   s:samplerstring - Choose a string to work with in this reaction - (SimpleSampler)
#   d:decomp - check if string is suitable for decomp if so decomp otherwise link
#   a:concat - join all strings in sample together
#   a:split - separate string at double letter
#   s:return - return sample to tank - (BruteSampler)
#   s:commit - return tank to set of tanks - (BruteSampler)
#   o:reaction - record tank used and that a reaction has occurred - (ClockObserver)
#   d:update - check if tanks have all been dealt with and enough reactions have been done - (CounterDecision)
#   s:transfers - randomly select a number of pairs of tanks and a number of strings to swap between them

# List of container nodes.rst:
#   T:tanks - set of all tanks in system
#   T:strings - set of initial strings to load
#   V:time - integer generation clock
#   T:tank - current tank of interest
#   S:composite - strings involved in reaction
#   V:reactions - tanks that have been used and total number of reactions


class StringCatLoadSampler(CoreNode.Sampler):
    """
    Loads system based on generating an initial population of strings.

    Parameters
    ----------

    containersin : None
    containersout : Tank
        Main tank used by StringCat chemistry
    readcontainers : None
    size : int
        Number of strings to be placed generated for each tank.
    tanks : int
        Number of tanks in the initial system.
    """

    def __init__(self, graph, containersin, containersout, readcontainers=None, size=1, tanks=1):
        super(StringCatLoadSampler, self).__init__(graph, containersin, containersout, readcontainers)
        self.size = size
        self.tanks = tanks
        self.sample = None
        pass

    def read(self):
        """
        Generates and reads in a random set of *size* random strings for each tank, where the number of tanks is
        *tanks*.

        """
        self.sample = [[random.choice(string.ascii_uppercase) for _ in range(0, self.size)] for _ in range(0,
                                                                                                           self.tanks)]

    def pull(self):
        self.containersin.remove(self.sample, full=True)
        pass

    def push(self):
        """
        Push set of tanks and strings to main tank.

        """
        self.containersout.add(self.sample, full=True)
        pass


class StringCatDecompDecision(CoreNode.Decision):
    """
    Node determines if decomposition occurs based on repeated letters.
    """

    def __init__(self, graph, options=2, readcontainers=None):
        super(StringCatDecompDecision, self).__init__(graph, options, readcontainers)
        self.samplestring = None
        pass

    def read(self):
        if self.readcontainers:
            self.samplestring = self.readcontainers.read()[0]

    def process(self):
        doubleindex = [i for i in range(0, len(self.samplestring) - 1)
                       if self.samplestring[i] == self.samplestring[i + 1]]
        if doubleindex:
            return 1
        else:
            return 0


class StringCatConcatAction(CoreNode.Action):

    def __init__(self, graph, writesample, readsample, readcontainers=None):
        super(StringCatConcatAction, self).__init__(graph, writesample, readsample, readcontainers)
        self.sample = []
        pass

    def read(self):
        self.sample = self.readsample.read()

    def pull(self):
        # print "pre-remove on pull"
        # print self.sample
        # print self.readsample.read()
        self.readsample.remove(self.sample)

    def check(self):
        return super(StringCatConcatAction, self).check()

    def process(self):
        # print self.sample
        self.sample = "".join(self.sample)
        # print self.sample
        pass

    def push(self):
        self.writesample.add(self.sample)


class StingCatSplitAction(CoreNode.Action):

    def __init__(self, graph, writesample, readsample, readcontainers=None):
        super(StingCatSplitAction, self).__init__(graph, writesample, readsample, readcontainers)
        self.sample = None

    def read(self):
        self.sample = self.readsample.read()[0]

    def pull(self):
        self.readsample.remove(self.sample)

    def check(self):
        return super(StingCatSplitAction, self).check()

    def process(self):
        doubleindex = [i for i in range(0, len(self.sample) - 1) if self.sample[i] == self.sample[i + 1]]
        index = random.choice(doubleindex)
        self.sample = [self.sample[0:index + 1], self.sample[index + 1:]]
        pass

    def push(self):
        self.writesample.add(self.sample)


class StringCatTransfersSampler(CoreNode.Sampler):

    def __init__(self, graph, containersin, containersout, readcontainers=None,
                 gridrows=1, gridcols=1, samplesize=1):
        super(StringCatTransfersSampler, self).__init__(graph, containersin, containersout, readcontainers)
        self.gridrows = gridrows
        self.gridcols = gridcols
        self.pairs = []
        self.samplesize = samplesize
        pass

    def read(self):
        super(StringCatTransfersSampler, self).read()

    def pull(self):
        sample = self.containersin.read()
        indices = list(range(0, self.gridcols * self.gridrows))
        pairs = []
        for cell in indices:
            neighbours = [cell + 1, cell - 1, cell + self.gridrows, cell - self.gridrows]
            # for checkcell in neighbours:
            neighbours = [x for x in neighbours if x in indices]
            # if checkcell not in indices:
            #     neighbours.remove(checkcell)
            if not neighbours:
                indices.remove(cell)
                continue
            othercell = random.choice(neighbours)
            indices.remove(othercell)
            indices.remove(cell)
            pairs.append([cell, othercell])
        for pair in pairs:
            try:
                sample0 = random.sample(sample[pair[1]], self.samplesize)
            except ValueError:
                sample0 = sample[pair[1]]
            self.containersin.remove(sample0, tank=pair[1])
            try:
                sample1 = random.sample(sample[pair[0]], self.samplesize)
            except ValueError:
                sample1 = sample[pair[0]]
            self.containersin.remove(sample1, tank=pair[0])
            self.sample.append([sample0, sample1])
        self.pairs = pairs
        pass

    def push(self):
        for i in range(0, len(self.pairs)):
            self.containersout.add(self.sample[i][0], tank=self.pairs[i][0])
            self.containersout.add(self.sample[i][1], tank=self.pairs[i][1])
        pass


class StringCatTank(CoreContainer.ListTank):

    def __init__(self, graph):
        super(StringCatTank, self).__init__(graph)
        self.list = []
        pass

    def read(self):
        return self.list[:]

    def add(self, particles=None):
        if self.list:
            if isinstance(particles[0], list):
                self.list = self.list + particles[0]
            else:
                self.list = self.list + particles
        elif isinstance(particles, list) and isinstance(particles[0], list):
            # print("nested")
            self.list = particles[0]
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print("List length")
        # print(len(self.list))
        return self.list

    def remove(self, particles=None):
        # print self.list
        # print particles.rst
        try:
            [self.list.remove(part) for part in particles]
        except ValueError:
            self.list.remove(particles)
        return self.list


class StringCatCommitSampler(CoreControl.BruteSampler):

    def __init__(self, graph, containersin, containersout, readcontainers=None):
        super(StringCatCommitSampler, self).__init__(graph, containersin, containersout, readcontainers)
        pass

    def read(self):
        super(StringCatCommitSampler, self).read()
        pass

    def pull(self):
        # print "pre-pull"
        super(StringCatCommitSampler, self).pull()
        # print self.sample
        pass

    def push(self):
        keys = self.containersout.dict.keys()
        for key in keys:
            if not self.containersout.dict[key]:
                self.containersout.add(self.sample, tank=key)
                break
