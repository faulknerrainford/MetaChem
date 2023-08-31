import csv
import random
import string

import networkx as nx

from metachem import Template, CoreNode, CoreContainer, CoreControl, Simulate
from metachem.StringCatChem import SCCBond


class WellMixedTank(Template):

    def __init__(self, bondgraph, sample_size=2, reactions=100, generations=10000, tank_size=1000, load_type=None,
                 log_node=None, load_file=None):
        super(WellMixedTank, self).__init__(bondgraph)
        # check bondgraph meets requirements for well mixed tank
        if not (
                bondgraph.count_control_in == 1 and bondgraph.count_control_out == 1 and bondgraph.count_links == 1):
            raise ValueError("WellMixedTank requires the bond graph have a single link container and a single in and "
                             "a single out control node")

        # generate graph with bondgraph connected

        # set up containers
        TTank = CoreContainer.ListTank(self.graph)
        self.tank = TTank
        TNew = CoreContainer.ListTank(self.graph)
        VTime = CoreContainer.StackEnvironment(self.graph)
        VTime.add(0)
        VGen = CoreContainer.StackEnvironment(self.graph)
        VGen.add(0)
        # connect SComposite to link containers
        SComposite = CoreContainer.ListSample(self.graph)
        for link in bondgraph.links:
            link.set_linknode(SComposite)
        # if log included add log environment
        VLog = CoreContainer.DictionaryEnvironment(self.graph)

        # set up control nodes

        sload = LoadSampler(self.graph, containersout=TTank, tank_size=tank_size,
                            load_type=load_type, load_file=load_file)
        self.start = sload
        ssample = CoreControl.SimpleSampler(self.graph, TTank, SComposite, size=sample_size)
        sreturn = CoreControl.BruteSampler(self.graph, SComposite, TNew)
        sgeneration = CoreControl.BruteSampler(self.graph, TNew, TTank)
        ssimulation = CoreControl.BruteSampler(self.graph, TNew, TTank)
        tterm = CoreNode.Termination(self.graph)
        otime = CoreControl.ClockObserver(self.graph, VTime, VTime)
        oreset = CoreControl.ClockResetObserver(self.graph, VGen, VGen)
        ogen = CoreControl.ClockObserver(self.graph, VGen, VGen)
        dgen = TimingsDecision(self.graph, [VGen, VTime, TTank], generations, reactions, sample_size)
        # if log_node given include
        if log_node:
            olog = log_node
            self.graph.add_node(olog)
        else:
            olog = TimeLoggerObserver(self.graph, [VTime, VGen], [VTime, VGen])

        # Creat stable graph edges
        edges = [[sload, otime], [otime, oreset], [oreset, ssample], [sreturn, ogen], [ogen, dgen], [dgen, ssample],
                 [dgen, sgeneration], [sgeneration, olog], [olog, otime], [dgen, ssimulation], [ssimulation, tterm]]

        # add edges to graph
        for edge in edges:
            self.graph.add_edge(edge[0], edge[1])

        # connect bonding graph
        self.graph = nx.compose(self.graph, bondgraph.graph)
        # connect control in and out
        self.graph.add_edge(ssample, bondgraph.control_in[0])
        self.graph.add_edge(bondgraph.control_out[0], sreturn)
        # connect link node
        bondgraph.links[0].set_linknode(SComposite)

    def print_tank(self):
        print(self.tank.read())


class LoadSampler(CoreNode.Sampler):

    def __init__(self, graph, containersout=None, tank_size=1000,
                 load_type="int", load_file=None):
        """
        Loads initial state of tank for the system. This can be read in from a csv file or it can generate a tank.
        Generated tanks can hold:
        'scc' - Uppercase letters
        'int' - integers from 0 to 100

        Parameters
        ----------
        graph           :   networkx.DiGraph
            Graph the node will be added to.
        containersout   :   Tank
            Tank for the generated or read in particles to be put into.
        tank_size       :   int
            Number of particles in the initial tank.
        load_type       :   String
            How the tank should be generated: read from csv (csv), generate uppercase letters (scc), generate ints (int)
        load_file       :   Stringmain block
            File path to csv file to read in
        """
        super(LoadSampler, self).__init__(graph, CoreNode.Sample(graph), containersout)
        self.load_file = load_file
        self.load_type = load_type
        self.tank_size = tank_size

    def read(self):
        """
        If reading from file reads in the information as a flat list.

        """
        # csv read
        if self.load_type == "csv":
            file = open(self.load_file, "r")
            self.sample = list(csv.reader(file, delimiter=","))[0]
            file.close()

    def pull(self):
        """
        Generates Tanks of the correct size if using generators.

        """
        # gen values if not read
        if self.load_type == "scc":
            self.sample = [random.choice(string.ascii_uppercase) for _ in range(0, self.tank_size)]
        elif self.load_type == "int":
            self.sample = [random.randint(0, 100) for _ in range(0, self.tank_size)]

    def push(self):
        """
        Pushes particles to tank.

        """
        # normal push
        self.containersout.add(self.sample)


class TimingsDecision(CoreNode.Decision):
    def __init__(self, graph, readcontainers, time_thresh, gen_thresh, sample_size):
        """
        Checks if enough bonds have been formed/attempted in the generation and if not returns 0. Else checks if the
        number of generations has reached the threshold for termination, if not returns 1 else returns 2.
        0 - loop to bonding
        1 - loop to new generation
        2 - terminate simulation run

        Parameters
        ----------
        graph           :   nx.DiGraph
            graph the decision node will be added to.
        readcontainers  :   list<Containers>
            [Bonding Count Environment, Generation Count Environment, Main Tank]
        time_thresh     :   int
            Number of generations before termination
        gen_thresh      :   int
            Number of uses of the bonding node/subgraph in each generation.
        """
        super(TimingsDecision, self).__init__(graph, 3, readcontainers)
        self.time_thresh = time_thresh
        self.gen_thresh = gen_thresh
        self.sample_size = sample_size
        self.time = 0
        self.gen = 0
        self.tank_size = 0

    def read(self):
        """
        Reads in the current times and bond count.

        """
        self.gen = self.readcontainers[0].read()[0]
        self.time = self.readcontainers[1].read()[0]
        self.tank_size = len(self.readcontainers[2].read())

    def process(self):
        """
        Compares thresholds and current values and selects an option.

        Returns
        -------
        int
            Option of which control edge to take from this control node.

        """
        if self.gen < self.gen_thresh and self.tank_size >= self.sample_size:
            return 0
        elif self.time < self.time_thresh:
            return 1
        else:
            return 2


class TimeLoggerObserver(CoreNode.Observer):
    """
    Prints out a statement of the current generation and number of reactions.

    Parameters
    -----------
    rewrite :   Boolean
        Whether the print statement should start a new line or write over the previous one.
    """

    def __init__(self, graph, containersin, containersout, readcontainers=None, rewrite=True):
        super(TimeLoggerObserver, self).__init__(graph, containersin, containersout, readcontainers)
        self.rewrite = rewrite
        self.clock = 0
        self.reactions = 0
        self.clock_container = containersin[0]
        self.reactions_container = containersin[1]
        pass

    def read(self):
        """
        Reads in value of clock and reactions.

        """
        self.clock = self.clock_container.read()[0]
        self.reactions = self.reactions_container.read()[0]
        pass

    def pull(self):
        pass

    def process(self):
        """
        Prints out the current clock and reactions
        """
        print("Currently in generation: " + str(self.clock) + " and completed " + str(self.reactions) + " reactions.",
              end='\r')
        pass

    def push(self):
        pass


if __name__ == "__main__":
    scc_bondgraph = SCCBond()
    reactor = WellMixedTank(scc_bondgraph, load_type="scc")
    sim = Simulate(reactor.graph, reactor.start)
    sim.run_graph()
    reactor.print_tank()
