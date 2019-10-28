import node
import random


class BruteSampler(node.Sampler):

    def __init__(self):
        super(BruteSampler, self).__init__()
        self.sample = []
        pass

    def read(self, info):
        super(BruteSampler, self).read(info)
        self.sample = self.containersin.read()

    def pull(self):
        self.containersin.remove(self.sample)
        pass

    def push(self):
        self.containersout.add(self.sample)
        pass


class SimpleSampler(node.Sampler):

    def __init__(self, size=1):
        super(SimpleSampler, self).__init__()
        self.size = size
        self.sample = []
        pass

    def read(self, info):
        super(SimpleSampler, self).read(info)
        self.sample = random.sample(self.containersin.read(), min(self.size, len(self.containersin.read())))


    def pull(self):
        [self.containersin.remove(elem) for elem in self.sample]
        pass

    def push(self):
        self.containersout.add(self.sample)
        pass


class OrderedSampler(node.Sampler):

    def __init__(self, n=1):
        super(OrderedSampler, self).__init__()
        self.sample = []
        self.size = n
        pass

    def read(self, info):
        super(OrderedSampler, self).read(info)
        self.sample = self.containersin.read()[0:self.size]

    def pull(self):
        self.containersin.remove(self.sample)
        pass

    def push(self):
        self.containersout.add(self.sample)
        pass


class ClockObserver(node.Observer):

    def __init__(self, increment=1):
            super(ClockObserver, self).__init__()
            self.increment = increment
            self.clock = 0
            pass

    def read(self, info):
        super(ClockObserver, self).read(info)
        if self.containersin != self.containersout:
            raise ValueError("ClockObserver must read and write to same container")
        self.clock = self.clock + self.increment
        pass

    def push(self):
        self.containersout.add(self.clock)
        pass


class CounterDecision(node.Decision):

    def __init__(self, options=2, threshold=1):
        if options == 2:
            super(CounterDecision, self).__init__(options)
            self.threshold = threshold
            self.check = 0
        else:
            raise ValueError("CounterDecision takes exactly two control options")
        pass

    def read(self, info):
        super(CounterDecision, self).read(info)
        self.check = self.readcontainers.read()[0]

    def process(self):
        if self.check >= self.threshold:
            return self.options[1]
        else:
            return self.options[0]


class EmptyDecision(node.Decision):

    def __init__(self, options=2):
        if options == 2:
            super(EmptyDecision, self).__init__(options)
        else:
            raise ValueError("CounterDecision takes exactly two control options")
        pass

    def read(self, info):
        super(EmptyDecision, self).read(info)
        if isinstance(self.readcontainers, list):
            raise TypeError("CounterDecision takes only a single readcontainer")
        self.check = self.readcontainers.read()

    def process(self):
        if self.check:
            return self.options[1]
        else:
            return self.options[0]
