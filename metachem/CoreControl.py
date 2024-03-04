import metachem.CoreNode as CoreNode
from metachem import CoreContainer
import random


class BruteSampler(CoreNode.Sampler):
    """
    Sampler that moves full content from one particle container to another.

    """

    def __init__(self, graph, containersin, containersout, readcontainers=None):
        super(BruteSampler, self).__init__(graph, containersin, containersout, readcontainers)
        self.sample = []
        pass

    def read(self):
        """
        Reads in a copy of all particles from the input container to sample list.
        """
        self.sample = self.containersin.read()

    def pull(self):
        """
        Removes all particles from the input container.
        """
        self.containersin.remove(self.sample)
        pass

    def push(self):
        """
        Adds all particles in sample to the output container.
        """
        self.containersout.add(self.sample)
        pass


class SimpleSampler(CoreNode.Sampler):
    """
    Takes a random uniformly distributed sample of a fixed size from the input container and moves it to an output
    container.

    Parameters
    ------------
    size: int
        Number of particles to be sampled and moved.
    """

    def __init__(self, graph, containersin, containersout, readcontainers=None, size=1):
        super(SimpleSampler, self).__init__(graph, containersin, containersout, readcontainers)
        self.size = size
        self.sample = []
        pass

    def read(self):
        """
        Reads a random selection of based on size from the input container without replacement into the internal sample.

        """
        if isinstance(self.containersin, CoreContainer.DictionaryTank) or \
                isinstance(self.containersin, CoreContainer.DictionaryEnvironment):
            self.sample = random.sample(list(self.containersin.read().values()),
                                        min(self.size, len(list(self.containersin.read().values()))))
        else:
            self.sample = random.sample(self.containersin.read(), min(self.size, len(self.containersin.read())))

    def pull(self):
        """
        Removes each of the particles in the sample from the input container.

        """
        [self.containersin.remove(elem) for elem in self.sample]
        pass

    def push(self):
        """
        Add the contents of the sample to the output container.

        """
        self.containersout.add(self.sample)
        pass


class OrderedSampler(CoreNode.Sampler):
    """
    Takes the first n elements from the input container and moves them to the output container.

    Parameters
    ----------
    n: int
        Number of particles to move.
    """

    def __init__(self, graph, containersin, containersout, readcontainers=None, n=1):
        super(OrderedSampler, self).__init__(graph, containersin, containersout, readcontainers)
        self.sample = []
        self.size = n
        pass

    def read(self):
        """
        Copies the first n particles from the input container to the internal sample.

        """
        self.sample = self.containersin.read()[0:self.size]

    def pull(self):
        """
        Removes the selected particles from the input container.

        """
        self.containersin.remove(self.sample)
        pass

    def push(self):
        """
        Adds the selected particles to the output container.

        """
        self.containersout.add(self.sample)
        pass


class ClockObserver(CoreNode.Observer):
    """
    Is connected to a clock container and increments a single variable by a fixed value.

    Parameters
    -----------
    increment : int
        The amount to be added to the variable. Default is 1.
    """

    def __init__(self, graph, containersin, containersout, readcontainers=None, increment=1):
        if containersin != containersout:
            raise ValueError("Clock must read and write to same variable")
        else:
            super(ClockObserver, self).__init__(graph, containersin, containersout, readcontainers)
            self.increment = increment
            self.clock = 0
            self.variable = self.containersin
            pass

    def read(self):
        """
        Reads in value of variable to clock.

        """
        self.clock = self.variable.read()[0]
        pass

    def pull(self):
        """
        Removes clock value from environment.

        """
        self.variable.remove(self.clock)

    def process(self):
        """
        Adds fixed increment to clock value.
        """
        self.clock = self.clock + self.increment
        pass

    def push(self):
        """
        Adds clock value to variable Environment.

        """
        self.variable.add(self.clock)
        pass


class ClockResetObserver(CoreNode.Observer):
    """
    Is connected to a clock container and resets value to reset value.

    Parameters
    -----------
    reset_value : int
        The amount in the clock when reset. Default is 0.
    """

    def __init__(self, graph, containersin, containersout, readcontainers=None, reset_value=1):
        if containersin != containersout:
            raise ValueError("Clock must read and write to same variable")
        else:
            super(ClockResetObserver, self).__init__(graph, containersin, containersout, readcontainers)
            self.reset_value = reset_value
            self.clock = 0
            self.variable = self.containersin
            pass

    def read(self):
        """
        Reads in value of variable to clock.

        """
        self.clock = self.variable.read()[0]
        pass

    def pull(self):
        """
        Removes clock value from environment.

        """
        self.variable.remove(self.clock)

    def process(self):
        """
        Resets clock value.
        """
        self.clock = self.reset_value
        pass

    def push(self):
        """
        Adds clock value to variable Environment.

        """
        self.variable.add(self.clock)
        pass


class CounterDecision(CoreNode.Decision):
    """
    Decides between default (normally loop) option and other option based on a single value and a threshold. Used
    generally for controlling length of a loop.

    Parameters
    -------------
    options : int
        Requires 2 control options to select from.
    threshold : int
        A fixed threshold value to test variable value against.
    readcontainers: ContainerNode
        A node with a value which will be checked.
    """

    def __init__(self, graph, options=2, readcontainers=None, threshold=1):
        if isinstance(readcontainers, list):
            raise TypeError("CounterDecision takes only a single read container")
        if options == 2:
            super(CounterDecision, self).__init__(graph, options, readcontainers)
            self.threshold = threshold
            self.check = 0
        else:
            raise ValueError("CounterDecision takes exactly two control options")
        pass

    def read(self):
        """
        Reads in value of Environment container to check.

        """
        self.check = self.readcontainers.read()[0]

    def process(self):
        """
        Check if the check equals or exceeds the threshold. If it does, we return a selection of option[1] from the set
        of possible pointer moves. Otherwise, the default option[0] is selected.

        """
        if self.check >= self.threshold:
            return self.options[1]
        else:
            return self.options[0]


class EmptyDecision(CoreNode.Decision):
    """
    Selects between two options based on if a container is empty. If it is empty we return the default first option but
    if not we return the second option.

    Parameters
    -------------
    options : int
        Requires 2 control options to choose between.
    readcontainers : ContainerNode
        The container node which, if empty, will affect the decision.
    """

    def __init__(self, graph, options=2, readcontainers=None):
        if isinstance(readcontainers, list):
            raise TypeError("CounterDecision takes only a single read container")
        if options == 2:
            super(EmptyDecision, self).__init__(graph, options, readcontainers)
        else:
            raise ValueError("CounterDecision takes exactly two control options")
        self.check = None

    def read(self):
        """
        Read in the contents of the read container (if any).

        """
        self.check = self.readcontainers.read()

    def process(self):
        """
        If there is content in check select option 1 else select option 0.
        """
        if self.check:
            return self.options[1]
        else:
            return self.options[0]
