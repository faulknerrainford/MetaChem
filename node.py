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

    def read(self):
        super(Termination, self).read()

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

    Attributes
    ----------
    writesample:    The sample node to which the node will push modified or new particles to. Must be a Sample.
    readsample:     The sample node from which the node will pull particles to modify or use in forming new particles. Must
                    be a Sample.
    readcontainers: Any other particle or environment containers the node needs to read from for it's process.

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
    def __init__(self, writesample, readsample, readcontainers=None):
        super(Action, self).__init__()
        if isinstance(readsample, list):
            for rs in readsample:
                if not isinstance(rs, ContainerNode) or isinstance(rs, Tank):
                    raise ValueError("Action can only read from Samples and Environments")
        elif isinstance(readsample, Tank) or not isinstance(readsample, ContainerNode):
            raise ValueError("Action can only read and write to Samples and Environments")
        if isinstance(writesample, list):
            for ws in writesample:
                if not isinstance(ws, ContainerNode) or isinstance(ws, Tank):
                    raise ValueError("Action can only write to Samples and Environments")
        elif isinstance(writesample, Tank) or not isinstance(writesample, ContainerNode):
            raise ValueError("Action can only read and write to Samples and Environments")
        if not isinstance(readsample, Sample) or not isinstance(readcontainers, ContainerNode) and readcontainers:
            raise ValueError("Action can only read from containers")
        self.writesample = writesample
        self.readsample = readsample
        self.readcontainers = readcontainers

    @abc.abstractmethod
    def check(self):
        return 0

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
    """
    A class for the basic Decision node. This node it used to branch control function. It does this by returning a
    number which is used to tell the graph handler which node to transition to next.

    ...

    Attributes
    ----------
    options: Integer indicating the number of outgoing graph edges.
    readcontainers: List of containers which are read to provide information to base decision on.

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
        return super(Decision, self).check()

    def pull(self):
        super(Decision, self).pull()

    def push(self):
        super(Decision, self).push()

    def transition(self):
        self.read()
        return self.process()


class Sampler(ControlNode):
    """
    A class for the basic description of a control node.

    ...

    Attributes
    ----------
    containersin: Containers from which the node can read and remove particles
    containersout: Containers from which the node can read and add particles
    readcontainers: Containers from which the node can read information
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
    containersin: Containers from which the node can read and remove.
    containersout: Containers from which the node can read and add.
    readcontainers: Containers from which the node can read only.
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
    def __init__(self, containersin, containersout, readcontainers=None, index=0):
        super(Observer, self).__init__()
        if containersin and not isinstance(containersin, ContainerNode) \
                and not all(isinstance(ci, ContainerNode) for ci in containersin) \
                or containersout and not isinstance(containersout, Environment) \
                and not all(isinstance(co, Environment) for co in containersout):
            raise ValueError("Observers can only read containers nodes and write to variables")
        self.containersin = containersin
        self.containersout = containersout
        if not isinstance(readcontainers, ContainerNode) and readcontainers and not isinstance(readcontainers, list):
            raise ValueError("Observer can only read from containers")
        elif isinstance(readcontainers, list) and not all(isinstance(rc, ContainerNode) for rc in readcontainers):
            raise ValueError("Observer can only read from containers")
        self.readcontainers = readcontainers
        self.index = index
        pass

    @abc.abstractmethod
    def read(self):
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
