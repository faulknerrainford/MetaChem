"""
Node module implements the core classes of MetaChem nodes. This includes the top level split between containers and
control as well as the specific classes of nodes used in implementing MetaChem graphs.

Classes
-------
ContainerNode
    Super class  for container nodes in MetaChem

ControlNode
    Super clas for control nodes in MetaChem

Termination
    Node which indicated to the graph handler to stop running transitioning between nodes. This node has no outgoing
    control edge.

Action
    Node which modifies particles in a sample. It has a single outgoing control edge.

Decision
    Node which branches control in the system. It has multiple outgoing control edges.

Sampler
    Node which moves particles between tanks and samples.

Observer
    Node which observes particles and environment and outputs information, sometimes summary statistics to the
    environment.

Tank
    Container node which holds particles which can not be edited.

Sample
    Container node which holds particles which can be edited.

Environment
    Container node which holds non-particle system and environment information.
"""
import abc
import random


class ContainerNode(object):
    """
    A class for the basic description of a container node.

    ...

    Attributes
    ----------
    id: unique number to identify container node

    Methods
    -------
    read()
        Required to be implemented in subclasses
    add(particles=None)
        Required to be implemented in subclasses
    remove(particles=None)
        Required to be implemented in subclasses
    """
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
    """
    A class for the basic description of a control node.

    ...

    Attributes
    ----------
    id: unique number to identify container node

    Methods
    -------
    transition()
        Used by graph to perform the algorithmic action of the node. It runs the transition functions including checking
        return from check function against a random number to allow for probabilistic execution of a nodes process.
    read()
        Required to be implemented in subclasses
    check()
        Required to be implemented in subclasses
    pull()
        Required to be implemented in subclasses
    process()
        Required to be implemented in subclasses
    push()
        Required to be implemented in subclasses

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        self.id = id(self)
        self.containersin = None
        self.containersout = None
        self.readcontainers = None
        pass

    def transition(self, info):
        self.read(info)
        if self.check() < random.random():
            self.pull()
            self.process()
            self.push()
        pass

    @abc.abstractmethod
    def read(self, info):
        [self.containersin, self.containersout, self.readcontainers] = info.graphdict[self]

    @abc.abstractmethod
    def check(self):
        return 0

    @abc.abstractmethod
    def pull(self):
        pass

    @abc.abstractmethod
    def process(self):
        pass

    @abc.abstractmethod
    def push(self):
        pass


class Termination(ControlNode):
    """
    A class for the Termination node which indicates to the graph handler to stop processing the graph.

    ...

    Methods
    -------
    read()
        Does nothing.
    check()
        Does nothing.
    pull()
        Does nothing.
    process()
        Does nothing.
    push()
        Does nothing.

    """

    def __init__(self):
        super(Termination, self).__init__()

    def read(self, info):
        super(Termination, self).read(info)

    def pull(self):
        super(Termination, self).pull()

    def check(self):
        super(Termination, self).check()

    def process(self):
        super(Termination, self).process()

    def push(self):
        super(Termination, self).push()


class Action(ControlNode):
    """
    A class for the basic description of a control node.

    ...

    Methods
    -------
    read()
        Required to be implemented in subclasses
    check()
        Required to be implemented in subclasses. Defaults to returning 0 so defaults to process happening.
    pull()
        Required to be implemented in subclasses
    process()
        Required to be implemented in subclasses
    push()
        Required to be implemented in subclasses

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(Action, self).__init__()

    @abc.abstractmethod
    def check(self):
        return 0

    @abc.abstractmethod
    def process(self):
        super(Action, self).process()
        
    @abc.abstractmethod
    def read(self, info):
        super(Action, self).read(info)
        
    @abc.abstractmethod
    def pull(self):
        super(Action, self).pull()

    @abc.abstractmethod
    def push(self):
        super(Action, self).push()


class Decision(ControlNode):
    """
    A class for the basic Decision node. This node it used to branch control function. It does this by returning a
    number which is used to tell the graph handler which node to transition to next.

    ...

    Attributes
    ----------
    options: Integer indicating the number of outgoing graph edges.

    Methods
    -------
    read()
        Required to be implemented in subclasses.
    check()
        Uses super function.
    pull()
        Does nothing.
    process()
        Required to be implemented in subclasses. Returns an integer indication which control edge to follow to next
        node. Defaults to returning 0.
    push()
        Does nothing.
    transition()
        Over writes normal transition function to return decision.

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, options=1):
        super(Decision, self).__init__()
        self.options = range(0, options)
        pass

    @abc.abstractmethod
    def read(self, info):
        super(Decision, self).read(info)

    @abc.abstractmethod
    def process(self):
        return self.options[0]

    def check(self):
        return super(Decision, self).check()

    def pull(self):
        super(Decision, self).pull()

    def push(self):
        super(Decision, self).push()

    def transition(self, info):
        self.read(info)
        return self.process()


class Sampler(ControlNode):
    """
    A class for the basic description of a control node.

    ...

    Attributes
    ----------
    sample: List for storing particles in while moving them between containers

    Methods
    -------
    read()
        Required to be implemented in subclasses.
    check()
        Defaults to return 0.
    pull()
        Required to be implemented in subclasses.
    process()
        Does nothing.
    push()
        Required to be implemented in subclasses.

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(Sampler, self).__init__()
        self.sample = []
        pass

    @abc.abstractmethod
    def read(self, info):
        super(Sampler, self).read(info)

    @abc.abstractmethod
    def pull(self):
        super(Sampler, self).pull()

    @abc.abstractmethod
    def push(self):
        super(Sampler, self).push()
        
    def check(self):
        return super(Sampler, self).check()
        
    def process(self):
        super(Sampler, self).process()


class Observer(ControlNode):
    """
    A class for the basic description of an observer node. These are used to update variables and generate summary
    statistics.

    ...

    Attributes
    ----------
    index: Used to indicate the need to read a particular variable in a list.

    Methods
    -------
    read()
        Required to be implemented in subclasses
    check()
        Returns 0 using default behavior.
    pull()
        Required to be implemented in subclasses
    process()
        Required to be implemented in subclasses
    push()
        Required to be implemented in subclasses

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, index=0):
        super(Observer, self).__init__()
        self.index = index
        pass

    @abc.abstractmethod
    def read(self, info):
        super(Observer, self).read(info)
        if self.readcontainers:
            if isinstance(self.readcontainers, ContainerNode):
                return self.readcontainers.read()
            else:
                return [rc.read() for rc in self.readcontainers]

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
        return super(Observer, self).check()


class Tank(ContainerNode):
    """
    A class for the basic description of a Tank particle container node. This one can not be connected as a writeable
    containers to an action.

    ...

    Methods
    -------
    read()
        Required to be implemented in subclasses
    add(particles=None)
        Required to be implemented in subclasses
    remove(particles=None)
        Required to be implemented in subclasses
    """
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
    """
    A class for the basic description of a Sample particle container node. This one can be connected as a writeable
    containers to an action.

    ...

    Methods
    -------
    read()
        Required to be implemented in subclasses
    add(particles=None)
        Required to be implemented in subclasses
    remove(particles=None)
        Required to be implemented in subclasses
    """

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
    """
    A class for the basic description of an environment node. This can container any information needed by the system.
    ...

    Methods
    -------
    read()
        Required to be implemented in subclasses
    add(particles=None)
        Required to be implemented in subclasses
    remove(particles=None)
        Required to be implemented in subclasses
    """

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
