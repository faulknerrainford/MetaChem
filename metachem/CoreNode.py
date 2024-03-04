#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# Created By  : Penn Faulkner Rainford
# Created Date: 17/08/2023
# version ='2.0'
# ---------------------------------------------------------------------------

"""
Node module implements the core classes of MetaChem nodes. This includes the top level split between containers and
control as well as the specific classes of nodes used in implementing MetaChem graphs.


"""
import abc
import random


class ContainerNode(object):
    """
    A super class for the basic description of a container node. Should instantiate a container suitable for the
    chemistries particles.

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, graph):
        self.id = id(self)
        self.graph = graph
        self.graph.add_node(self)

    @abc.abstractmethod
    def read(self):
        """
        Abstract method required to be implemented in subclasses. Should return without modification a copy of 1 or
        more particles in the container.
        -------

        Returns
        -------
        list of objects
            List of copied particles from the container.
        """
        pass

    @abc.abstractmethod
    def add(self, particles=None):
        """
        Abstract method required to be implemented in subclasses. Should add provided particles to container.

        Parameters
        ----------
        particles : list of objects
            Particle object relating to particular chemistry

        """
        pass

    @abc.abstractmethod
    def remove(self, particles=None):
        """
        Abstract method required to be implemented in subclasses. Should remove given set of particles from container.

        Parameters
        ----------
        particles : list of objects
            List of particle objects relating to particular chemistry

        """
        pass


class ControlNode(object):
    """
    A super class for the basic description of a control node.

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, graph):
        self.id = id(self)
        self.graph = graph
        self.graph.add_node(self)
        pass

    def transition(self):
        """
        Used by graph to perform the algorithmic action of the node. It runs the transition functions including checking
        return from check function against a random number to allow for probabilistic execution of a nodes process.

        """
        self.read()
        if self.check() < random.random():
            self.pull()
            self.process()
            self.push()
        pass

    @abc.abstractmethod
    def read(self):
        """
        An abstract method which must be implemented in subclasses. Should not edit any containers. No return.
        """
        pass

    @abc.abstractmethod
    def check(self):
        """
        An abstract method which must be implemented in subclasses. Only overridden in Action nodes.

        """
        return 0

    @abc.abstractmethod
    def pull(self):
        """
        An abstract method which must be implemented in subclasses. Used to pull information and particles from
        containers.

        """
        pass

    @abc.abstractmethod
    def process(self):
        """
        An abstract method which must be implemented in subclasses. Does not edit containers but processes the data with
        in the node.

        """
        pass

    @abc.abstractmethod
    def push(self):
        """
        An abstract method which must be implemented in subclasses. Used to push data and particles to containers.

        """
        pass


class Termination(ControlNode):
    """
    A class for the Termination node which indicates to the graph handler to stop processing the graph.

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    """

    def __init__(self, graph):
        super(Termination, self).__init__(graph)

    def read(self):
        """
        Does nothing.
        """
        super(Termination, self).read()

    def pull(self):
        """
        Does nothing.
        """
        super(Termination, self).pull()

    def check(self):
        """
        Does nothing.
        """
        super(Termination, self).check()

    def process(self):
        """
        Does nothing.
        """
        super(Termination, self).process()

    def push(self):
        """
        Does nothing.
        """
        super(Termination, self).push()


# noinspection SpellCheckingInspection
class Action(ControlNode):
    """
    A class for the basic description of an action control node.

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    writesample: Sample
        The sample node to which the node will push modified or new particles to. Must be a Sample.
    readsample:  Sample
        The sample node from which the node will pull particles to modify or use in forming new particles.
        Must be a Sample.
    readcontainers: list(ContainerNode)
        Any other particle or environment containers the node needs to read from for its process.

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, graph, writesample, readsample, readcontainers=None):
        super(Action, self).__init__(graph)
        # type check inputs
        if isinstance(readsample, list):
            for rs in readsample:
                if not isinstance(rs, ContainerNode) or isinstance(rs, Tank):
                    raise ValueError("Action can only read from Samples and Environments")
                if rs not in list(self.graph.nodes):
                    raise ValueError("Cannot connect to container not in graph")
        elif isinstance(readsample, Tank) or not isinstance(readsample, ContainerNode):
            raise ValueError("Action can only read and write to Samples and Environments")
        elif readsample not in list(self.graph.nodes):
            raise ValueError("Cannot connect to container not in graph")
        if isinstance(writesample, list):
            for ws in writesample:
                if not isinstance(ws, ContainerNode) or isinstance(ws, Tank):
                    raise ValueError("Action can only write to Samples and Environments")
                if ws not in list(self.graph.nodes):
                    raise ValueError("Cannot connect to conatiner not in graph")
        elif isinstance(writesample, Tank) or not isinstance(writesample, ContainerNode):
            raise ValueError("Action can only read and write to Samples and Environments")
        elif writesample not in list(self.graph.nodes):
            raise ValueError("Cannot connect to container not in graph")
        if not isinstance(readsample, Sample) or not isinstance(readcontainers, ContainerNode) and readcontainers:
            raise ValueError("Action can only read from containers")
        if isinstance(readcontainers, list):
            for rc in readcontainers:
                if not isinstance(rc, ContainerNode):
                    raise ValueError("Action can only read from containers")
                elif rc not in list(self.graph.nodes):
                    raise ValueError("Cannot connect to container not in graph")
        elif readcontainers and readcontainers not in list(self.graph.nodes):
            raise ValueError("Cannot connect to container not in graph")
        # add edges from node to write samples
        self.writesample = writesample
        if isinstance(writesample, list):
            for ws in writesample:
                self.graph.add_edge(self, ws)
        else:
            self.graph.add_edge(self, writesample)
        # add edges from read samples to node
        self.readsample = readsample
        if isinstance(readsample, list):
            for rs in readsample:
                self.graph.add_edge(rs, self)
        else:
            self.graph.add_edge(readsample, self)
        # add edges from read containers to node
        self.readcontainers = readcontainers
        if isinstance(readcontainers, list):
            for rc in readcontainers:
                self.graph.add_edge(rc, self)
        elif readcontainers:
            self.graph.add_edge(readcontainers, self)

    @abc.abstractmethod
    def check(self):
        """
        Required to be implemented in subclasses. Defaults to returning 0 so defaults to process happening.

        """
        return 0

    @abc.abstractmethod
    def process(self):
        """
        Required to be implemented in subclasses

        """
        super(Action, self).process()

    @abc.abstractmethod
    def read(self):
        """
        Required to be implemented in subclasses

        """
        super(Action, self).read()

    @abc.abstractmethod
    def pull(self):
        """
        Required to be implemented in subclasses

        """
        super(Action, self).pull()

    @abc.abstractmethod
    def push(self):
        """
        Required to be implemented in subclasses

        """
        super(Action, self).push()


class Decision(ControlNode):
    """
    A class for the basic Decision node. This node it used to branch control function. It does this by returning a
    number which is used to tell the graph handler which node to transition to next.

    ...

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    options : int or range
        Integer indicating the number of outgoing graph edges.(Reset to range on setup)
    readcontainers : list(ContainerNode)
        ContainerNodes read to provide information to base decision on.


    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, graph, options=1, readcontainers=None):
        super(Decision, self).__init__(graph)
        # type check inputs
        if readcontainers:
            if isinstance(readcontainers, list):
                for rc in readcontainers:
                    if not isinstance(rc, ContainerNode):
                        raise ValueError("Decision can only read from containers")
                    elif rc not in list(self.graph.nodes):
                        raise ValueError("Cannot connect to container not in graph")
            elif not isinstance(readcontainers, ContainerNode):
                raise ValueError("Decision can only read from containers")
            elif readcontainers not in list(self.graph.nodes):
                raise ValueError("Cannot connect to container not in graph")
            self.options = range(0, options)
            # add edges from read containers to node
            self.readcontainers = readcontainers
            if isinstance(readcontainers, list):
                for rc in readcontainers:
                    self.graph.add_edge(self, rc)
            else:
                self.graph.add_edge(self, readcontainers)
        pass

    @abc.abstractmethod
    def read(self):
        """
        Required to be implemented in subclasses.

        """
        super(Decision, self).read()

    @abc.abstractmethod
    def process(self):
        """

        Required to be implemented in subclasses. Returns an integer indication which control edge to follow to next
        node. Defaults to returning 0.

        """
        return self.options[0]

    def check(self):
        """

        Uses super function.

        """
        return super(Decision, self).check()

    def pull(self):
        """

        Does nothing.

        """
        super(Decision, self).pull()

    def push(self):
        """

        Does nothing.

        """
        super(Decision, self).push()

    def transition(self):
        """

        Overwrites normal transition function to return decision.

        """
        self.read()
        return self.process()


class Sampler(ControlNode):
    """
    A class for the basic description of a control node.

    ...

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    containersin: list(ContainerNode)
        Containers from which the node can read and remove particles, only Tanks and Samplers
    containersout: list(ContainerNode)
        Containers from which the node can read and add particles, only Tanks and Samplers
    readcontainers: list(ContainerNode)
        Containers from which the node can read information

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, graph, containersin, containersout, readcontainers=None):
        super(Sampler, self).__init__(graph)
        if isinstance(containersout, list):
            for co in containersout:
                if not isinstance(co, Tank) and not isinstance(co, Sample):
                    raise ValueError("Sampler can only push to particle containers")
                if co not in list(self.graph.nodes):
                    raise ValueError("Cannot connect to container not in graph")
        elif isinstance(containersin, list):
            for ci in containersin:
                if not isinstance(ci, Tank) or not isinstance(ci, Sample):
                    raise ValueError("Sampler can only pull from containers")
                if ci not in list(self.graph.nodes):
                    raise ValueError("Cannot connect to container not in graph")
        elif not isinstance(containersout, ContainerNode) or not isinstance(containersin, ContainerNode):
            raise ValueError("Sampler can only push and pull from containers")
        elif isinstance(containersin, Environment) or isinstance(containersout, Environment):
            raise ValueError("Sample can only push and pull from particle containers")
        elif (containersin not in list(self.graph.nodes)) or (containersout not in list(self.graph.nodes)):
            raise ValueError("Cannot connect to container not in graph")
        # add edge from containers in to node
        self.containersin = containersin
        if isinstance(containersin, list):
            for ci in containersin:
                self.graph.add_edge(ci, self)
        else:
            self.graph.add_edge(containersin, self)
        # add edge from node to containers out
        self.containersout = containersout
        if isinstance(containersout, list):
            for co in containersout:
                self.graph.add_edge(self, co)
        else:
            self.graph.add_edge(self, containersout)
        # add edge from read containers to node
        self.readcontainers = readcontainers
        if isinstance(readcontainers, list):
            for rc in readcontainers:
                self.graph.add_edge(self, rc)
        elif readcontainers:
            self.graph.add_edge(self, readcontainers)
        self.sample = []
        pass

    @abc.abstractmethod
    def read(self):
        """

        Required to be implemented in subclasses.

        """
        super(Sampler, self).read()

    @abc.abstractmethod
    def pull(self):
        """

        Required to be implemented in subclasses.

        """
        super(Sampler, self).pull()

    @abc.abstractmethod
    def push(self):
        """

        Required to be implemented in subclasses.

        """
        super(Sampler, self).push()

    def check(self):
        """

        Defaults to return 0.

        """
        return super(Sampler, self).check()

    def process(self):
        """

        Does nothing.

        """
        super(Sampler, self).process()


class Observer(ControlNode):
    """
    A class for the basic description of an observer node. These are used to update variables and generate summary
    statistics.

    ...

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    containersin: list(Environment)
        Containers from which the node can read and remove.
    containersout: list(Environment)
        Containers from which the node can read and add.
    readcontainers: list(ContainerNode)
        Containers from which the node can read only.
    index: int
        Used to indicate the need to read a particular variable in a list.

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, graph, containersin, containersout, readcontainers=None, index=0):
        super(Observer, self).__init__(graph)
        # type check inputs
        if isinstance(containersout, list):
            for co in containersout:
                if not isinstance(co, Environment):
                    raise ValueError("Observer can only push to Environment")
                if co not in list(self.graph.nodes):
                    raise ValueError("Cannot connect to container not in graph")
        if isinstance(containersin, list):
            for ci in containersin:
                if not isinstance(ci, Environment):
                    raise ValueError("Observer can only pull from Environment")
                if ci not in list(self.graph.nodes):
                    raise ValueError("Cannot connect to container not in graph")
        elif containersin and not isinstance(containersin, ContainerNode) \
                and not all(isinstance(ci, ContainerNode) for ci in containersin) \
                or containersout and not isinstance(containersout, Environment) \
                and not all(isinstance(co, Environment) for co in containersout):
            raise ValueError("Observers can only read containers nodes and write to variables")
        elif (containersin not in list(self.graph.nodes) or (containersout not in list(self.graph.nodes))):
            raise ValueError("Cannot connect to container not in graph")
        self.containersin = containersin
        self.containersout = containersout
        if not isinstance(readcontainers, ContainerNode) and readcontainers and not isinstance(readcontainers, list):
            raise ValueError("Observer can only read from containers")
        elif isinstance(readcontainers, list) and not all(isinstance(rc, ContainerNode) for rc in readcontainers):
            raise ValueError("Observer can only read from containers")
        elif isinstance(readcontainers, list) and not all(rc in list(self.graph.nodes) for rc in readcontainers):
            raise ValueError("Cannot connect to containers not in graph")
        elif readcontainers  and readcontainers not in list(self.graph.nodes):
            raise ValueError("Cannot connect to containers not in graph")
        # add edges from read containers to node
        self.readcontainers = readcontainers
        if isinstance(readcontainers, list):
            for rc in readcontainers:
                self.graph.add_edge(self, rc)
        elif readcontainers:
            self.graph.add_edge(self, readcontainers)
        self.index = index
        pass

    @abc.abstractmethod
    def read(self):
        """

        Required to be implemented in subclasses. Defaults to reading all read containers.

        """
        if isinstance(self.readcontainers, ContainerNode):
            return self.readcontainers.read()
        else:
            return [rc.read() for rc in self.readcontainers]

    @abc.abstractmethod
    def process(self):
        """

        Required to be implemented in subclasses

        """
        super(Observer, self).process()

    @abc.abstractmethod
    def push(self):
        """

        Required to be implemented in subclasses

        """
        super(Observer, self).push()

    @abc.abstractmethod
    def pull(self):
        """

        Required to be implemented in subclasses

        """
        super(Observer, self).pull()

    def check(self):
        """

        Returns 0 using default behavior.

        """
        return super(Observer, self).check()


class Tank(ContainerNode):
    """
    A class for the basic description of a Tank particle container node. This one can not be connected as a writeable
    containers to an action.

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, graph):
        super(Tank, self).__init__(graph)
        pass

    @abc.abstractmethod
    def read(self):
        """
        Required to be implemented in subclasses. Should return a copy of some or all of the container
        """
        pass

    @abc.abstractmethod
    def add(self, particles=None):
        """
        Required to be implemented in subclasses.

        Parameters
        ----------
        particles : List<Particle>
            List of particles to be added to the container

        """
        pass

    @abc.abstractmethod
    def remove(self, particles=None):
        """
        Required to be implemented in subclasses.

        Parameters
        ----------
        particles : List<Particle>
            List of particles to be removed from the container

        """
        pass


class Sample(ContainerNode):
    """
    A class for the basic description of a Sample particle container node. This one can be connected as a writeable
    containers to an action.

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, graph):
        super(Sample, self).__init__(graph)
        pass

    @abc.abstractmethod
    def read(self):
        """
        Required to be implemented in subclasses. Should return a copy of some or all of the container
        """
        pass

    @abc.abstractmethod
    def add(self, particles=None):
        """
        Required to be implemented in subclasses.

        Parameters
        ----------
        particles : List<Particle>
            List of particles to be added to the container

        """
        pass

    @abc.abstractmethod
    def remove(self, particles=None):
        """
        Required to be implemented in subclasses.

        Parameters
        ----------
        particles : List<Particle>
            List of particles to be removed from the container

        """
        pass


class Environment(ContainerNode):
    """
    A class for the basic description of an environment node. This can container any information needed by the system.

    Parameters
    ----------
    graph   :   nx.DiGraph
        graph the node is inserted in.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, graph):
        super(Environment, self).__init__(graph)
        pass

    @abc.abstractmethod
    def read(self):
        """
        Required to be implemented in subclasses. Should return a copy of some or all of the variables in the container.
        """
        pass

    @abc.abstractmethod
    def add(self, variables=None):
        """
        Required to be implemented in subclasses.

        Parameters
        ----------
        variables
            List (or dictionary) of variables (variable name: variable value pairs) to be added to the container.

        """
        pass

    @abc.abstractmethod
    def remove(self, variables=None):
        """
        Required to be implemented in subclasses.

        Parameters
        ----------
        variables
            List (or dictionary) of variables (variable name: variable value pairs) to be removed from the container.

        """
        pass
