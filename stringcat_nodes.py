import node
import string
import random
import container
import control

# List of needed control nodes:
#   s:load - input set of strings
#   o:time - increments time between generations - (ClockObserver)
#   s:samplertank - Chooses a tank to work over that hasn't been chosen in the current generation - (SimpleSampler)
#   s:samplerstring - Choose a string to work with in this reaction - (SimpleSampler)
#   d:decomp - check if string is suitable for decomp if so decomp otherwise link
#   a:concat - join all strings in sample together
#   a:split - seperate string at double letter
#   s:return - return sample to tank - (BruteSampler)
#   s:commit - return tank to set of tanks - (BruteSampler)
#   o:reaction - record tank used and that a reaction has occurred - (ClockObserver)
#   d:update - check if tanks have all been dealt with and enough reactions have been done - (CounterDecision)
#   s:transfers - randomly select a number of pairs of tanks and a number of strings to swap between them

# List of container nodes:
#   T:tanks - set of all tanks in system
#   T:strings - set of initial strings to load
#   V:time - integer generation clock
#   T:tank - current tank of interest
#   S:composite - strings involved in reaction
#   V:reactions - tanks that have been used and total number of reactions


class StringCatLoadSampler(node.Sampler):

    def __init__(self, containersin, containersout, readcontainers=None, size=1, tanks=1):
        super(StringCatLoadSampler, self).__init__(containersin, containersout, readcontainers)
        self.size = size
        self.tanks = tanks
        self.sample = None
        pass

    def read(self):
        self.sample = [[random.choice(string.uppercase) for _ in range(0, self.size)] for _ in range(0, self.tanks)]

    def pull(self):
        self.containersin.remove(self.sample)
        pass

    def push(self):
        self.containersout.add(self.sample)
        pass


class StringCatDecompDecision(node.Decision):

    def __init__(self, options=2, readcontainers=None):
        super(StringCatDecompDecision, self).__init__(options, readcontainers)
        self.samplestring = None
        pass

    def read(self):
        self.samplestring = self.readcontainers.read()

    def process(self):
        doubleindex = [i for i in range(0, len(self.samplestring) - 1)
                       if self.samplestring[i] == self.samplestring[i + 1]]
        if doubleindex:
            return 1
        else:
            return 0


class StringCatConcatAction(node.Action):

    def __init__(self, writesample, readsample, readcontainers=None):
        super(StringCatConcatAction, self).__init__(writesample, readsample, readcontainers)
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
        super(StringCatConcatAction, self).check()

    def process(self):
        # print self.sample
        self.sample = "".join(self.sample)
        # print self.sample
        pass

    def push(self):
        self.writesample.add(self.sample)


class StingCatSplitAction(node.Action):

    def __init__(self, writesample, readsample, readcontainers=None):
        super(StingCatSplitAction, self).__init__(writesample, readsample, readcontainers)
        self.sample = None
        pass

    def read(self):
        self.sample = self.readsample.read()

    def pull(self):
        self.readsample.remove(self.sample)

    def check(self):
        super(StingCatSplitAction, self).check()

    def process(self):
        doubleindex = [i for i in range(0, len(self.sample) - 1) if self.sample[i] == self.sample[i+1]]
        index = random.choice(doubleindex)
        self.sample = [self.sample[0:index], self.sample[index:0]]
        self.writesample.add(self.sample)
        pass

    def push(self):
        self.writesample.add(self.sample)


class StringCatTransfersSampler(node.Sampler):

    def __init__(self, containersin, containersout, readcontainers=None,
                 gridrows=1, gridcols=1, samplesize=1):
        super(StringCatTransfersSampler, self).__init__(containersin, containersout, readcontainers)
        self.gridrows = gridrows
        self.gridcols = gridcols
        self.pairs = []
        self.samplesize = samplesize
        pass

    def read(self):
        super(StringCatTransfersSampler, self).read()

    def pull(self):
        sample = self.containersin[0].read()
        indices = range(0, self.gridcols*self.gridrows)
        pairs = []
        for cell in indices:
            neighbours = [cell+1, cell-1, cell+self.gridrows, cell-self.gridrows]
            for checkcell in neighbours:
                if checkcell not in indices:
                    neighbours.remove(checkcell)
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
            self.containersin[0][pair[1]].remove(sample0)
            try:
                sample1 = random.sample(sample[pair[0]], self.samplesize)
            except ValueError:
                sample1 = sample[pair[0]]
            self.containersin[0][pair[0]].remove(sample1)
            self.sample.append([sample0, sample1])
        self.pairs = pairs
        pass

    def push(self):
        for i in range(0, len(self.pairs)):
            self.containersout[0, self.pairs[i][0]].append(self.sample[i][0])
            self.containersout[0, self.pairs[i][1]].append(self.sample[i][1])
        pass


class StringCatTank(container.ListTank):

    def __init__(self):
        super(StringCatTank, self).__init__()
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
            # print "nested"
            self.list = particles[0]
        elif isinstance(particles, list):
            self.list = particles
        else:
            self.list = [particles]
        # print "List length"
        # print len(self.list)
        return self.list

    def remove(self, particles=None):
        # print self.list
        # print particles
        try:
            [self.list.remove(part) for part in particles]
        except ValueError:
            self.list.remove(particles)
        return self.list


class StringCatCommitSampler(control.BruteSampler):

    def __init__(self, containersin, containersout, readcontainers=None):
        super(StringCatCommitSampler, self).__init__(containersin, containersout, readcontainers)
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
        self.containersout.add([self.sample])
        pass
