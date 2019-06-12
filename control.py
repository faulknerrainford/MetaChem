import node
import random


class BruteSampler(node.Sampler):

    def __init__(self, containersin, containersout, readcontainers=None):
        super(BruteSampler, self).__init__(containersin, containersout, readcontainers)
        self.sample = []
        pass

    def read(self):
        self.sample = self.containersin.read()

    def pull(self):
        self.containersin.remove(self.sample)
        pass

    def push(self):
        self.containersout.add(self.sample)
        pass


class SimpleSampler(node.Sampler):

    def __init__(self, containersin, containersout, readcontainers=None, size=1):
        super(SimpleSampler, self).__init__(containersin, containersout, readcontainers)
        self.size = size
        self.sample = []
        pass

    def read(self):
        self.sample = random.sample(self.containersin.read(), min(self.size, len(self.containersin.read())))

    def pull(self):
        [self.containersin.remove(elem) for elem in self.sample]
        pass

    def push(self):
        self.containersout.add(self.sample)
        pass

class OrderedSampler(node.Sampler):

    def __init__(self, containersin, containersout, readcontainers=None, n=1):
        super(FirstSampler, self).__init__(containersin, containersout, readcontainers)
        self.sample = []
        self.size = n
        pass

    def read(self):
        self.sample = self.containersin.read()[0:self.size]

    def pull(self):
        self.containersin.remove(self.sample)
        pass

    def push(self):
        self.containersout.add(self.sample)
        pass



class ClockObserver(node.Observer):

    def __init__(self, containersin, containersout, readcontainers=None, increment=1):
        if containersin != containersout:
            raise ValueError("Clock must read and write to same variable")
        else:
            super(ClockObserver, self).__init__(containersin, containersout, readcontainers)
            self.increment = increment
            self.clock = 0
            self.variable = self.containersin
            pass

    def read(self):
        self.clock = self.variable.read()[0]
        pass

    def pull(self):
        self.variable.remove(self.clock)

    def process(self):
        self.clock = self.clock + self.increment
        pass

    def push(self):
        self.variable.add(self.clock)
        pass


class CounterDecision(node.Decision):

    def __init__(self, options=2, readcontainers=None, threshold=1):
        if isinstance(readcontainers, list):
            raise TypeError("CounterDecision takes only a single readcontainer")
        if options == 2:
            super(CounterDecision, self).__init__(options, readcontainers)
            self.threshold = threshold
            self.check = 0
        else:
            raise ValueError("CounterDecision takes exactly two control options")
        pass

    def read(self):
        self.check = self.readcontainers.read()

    def process(self):
        if self.check >= self.threshold:
            return self.options[1]
        else:
            return self.options[0]
