import abc
import random


class ContainerNode(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        self.id = id(self)
        pass

    @abc.abstractmethod
    def read(self):
        pass

    @abc.abstractmethod
    def add(self, particles=None):
        pass

    @abc.abstractmethod
    def remove(self, particles=None):
        pass


class ControlNode(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        self.id = id(self)
        pass

    def transition(self):
        self.read()
        if self.check() < random.random():
            self.pull()
            self.process()
            self.push()
        pass

    @abc.abstractmethod
    def read(self):
        pass

    @abc.abstractmethod
    def check(self):
        return 1

    @abc.abstractmethod
    def pull(self):
        pass

    @abc.abstractmethod
    def process(self):
        pass

    @abc.abstractmethod
    def push(self):
        pass


class Action(ControlNode):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, writesample, readsample, readcontainers=None):
        super(Action, self).__init__()
        if not isinstance(writesample, Sample) or not isinstance(readsample, Sample):
            raise ValueError("Action can only read and write to Samples")
        if not isinstance(readsample, Sample) or not isinstance(readcontainers, ContainerNode) and readcontainers:
            raise ValueError("Action can only read from containers")
        self.writesample = writesample
        self.readsample = readsample
        self.readcontainers = readcontainers

    @abc.abstractmethod
    def check(self):
        return super(Action, self).check()

    @abc.abstractmethod
    def process(self):
        super(Action, self).process()
        
    @abc.abstractmethod
    def read(self):
        super(Action, self).read()
        
    @abc.abstractmethod
    def pull(self):
        super(Action, self).pull()

    @abc.abstractmethod
    def push(self):
        super(Action, self).push()


class Decision(ControlNode):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, options=1, readcontainers=None):
        super(Decision, self).__init__()
        if not isinstance(readcontainers, ContainerNode):
            raise ValueError("Decision can only read from containers")
        self.options = range(0, options)
        self.readcontainers = readcontainers
        pass

    @abc.abstractmethod
    def read(self):
        super(Decision, self).read()

    @abc.abstractmethod
    def process(self):
        return self.options[0]

    def check(self):
        super(Decision, self).check()

    def pull(self):
        super(Decision, self).pull()

    def push(self):
        super(Decision, self).push()

    def transition(self):
        self.read()
        return self.process()


class Sampler(ControlNode):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, containersin, containersout, readcontainers=None):
        super(Sampler, self).__init__()
        if not isinstance(containersout, ContainerNode) or not isinstance(containersin, ContainerNode):
            raise ValueError("Sampler can only push and pull from containers")
        else:
            if isinstance(containersin, Environment) or isinstance(containersout, Environment):
                raise ValueError("Sample can only push and pull from particle containers")
        self.containersin = containersin
        self.containersout = containersout
        self.readcontainers = readcontainers
        self.sample = []
        pass

    @abc.abstractmethod
    def read(self):
        super(Sampler, self).read()

    @abc.abstractmethod
    def pull(self):
        super(Sampler, self).pull()

    @abc.abstractmethod
    def push(self):
        super(Sampler, self).push()
        
    def check(self):
        super(Sampler, self).check()
        
    def process(self):
        super(Sampler, self).process()


class Observer(ControlNode):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, containersin, containersout, readcontainers=None, index=0):
        super(Observer, self).__init__()
        if not isinstance(containersin, ContainerNode) or not isinstance(containersout, Environment):
            raise ValueError("Observers can only read containers nodes and write to variables")
        self.containersin = containersin
        self.containersout = containersout
        if not isinstance(readcontainers, ContainerNode) and readcontainers:
            raise ValueError("Observer can only read from containers")
        self.readcontainers = readcontainers
        self.index = index
        pass

    @abc.abstractmethod
    def read(self):
        return self.readcontainers.read()

    @abc.abstractmethod
    def process(self):
        super(Observer, self).process()

    @abc.abstractmethod
    def push(self):
        super(Observer, self).push()

    @abc.abstractmethod
    def pull(self):
        super(Observer, self).pull()

    def check(self):
        super(Observer, self).check()


class Tank(ContainerNode):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(Tank, self).__init__()
        pass

    @abc.abstractmethod
    def read(self):
        pass

    @abc.abstractmethod
    def add(self, particles=None):
        pass

    @abc.abstractmethod
    def remove(self, particles=None):
        pass


class Sample(ContainerNode):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(Sample, self).__init__()
        pass

    @abc.abstractmethod
    def read(self):
        pass

    @abc.abstractmethod
    def add(self, particles=None):
        pass

    @abc.abstractmethod
    def remove(self, particles=None):
        pass


class Environment(ContainerNode):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Environment, self).__init__()
        pass

    @abc.abstractmethod
    def read(self):
        pass

    @abc.abstractmethod
    def add(self, variables=None):
        pass

    @abc.abstractmethod
    def remove(self, variables=None):
        pass
