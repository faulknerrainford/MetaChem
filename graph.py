"""
Graph module is designed to handle and run MetaChem graphs, see Rainford et. al. 2019. It currently only creates and
implements basic static MetaChem Graphs with all data preloaded and the information graph formed during control node
instantiation. Later efforts will modify control node class to allow node fuction to be declared and the information
links added separately. This will require the additional processing of the information links to be implemented in the
graph object.

Classes
-------
Graph
    The class describing a static MetaChem graph with capability to run the graph.
"""
import node


class Graph(object):
    """
    A Class for describing and running MetaChem graphs

    ...

    Attributes
    ----------
    controledges : List of lists of control node pairs
        This is the raw input control graph provided to the system, information graph is declared when instantiating
        control nodes. TO DO: Instantiate nodes based on an information graph input
    graphdict : Dictionary
        In this dictionary keys are control nodes and values are control nodes or lists of control nodes (default empty)
    verbose : Boolean
        Controls console output for debugging

    Methods
    -------
    check_graph()
        Checks the input graph conforms to all MetaChem rules
    run_graph(pointer, inputtank=None, transitionlimit=0)
        Runs the graph with containers primed with the inputtank. The graph will perform a number of state transitions
        equal to the transition limit.
    """

    def __init__(self, controledges, verbose=False):
        """
        Parameters
        ----------
        controledges: List of lists of pairs of control nodes
            Used to define the MetaChem control graph
        verbose:  Boolean
            Used to control console output for debugging (default False)
        """

        self.controledges = controledges
        self.graphdict = {}
        self.verbose = verbose
        for edge in self.controledges:
            if edge[0] in self.graphdict:
                try:
                    self.graphdict[edge[0]] = self.graphdict[edge[0]]+[edge[1]]
                except TypeError:
                    self.graphdict[edge[0]] = [self.graphdict[edge[0]]]+[edge[1]]
            else:
                self.graphdict[edge[0]] = edge[1]   # Dictionary of node edge destinations indexed by source
        self.check_graph()
        pass

    def check_graph(self):
        """
        Function to check the input graph meets the specification of a MetaChem graph

        ...

        Raises
        -------
        ValueError("All edges must be between control nodes")
            If the graph is incorrect a value error is raised to inform the user that the control graph is invalid
        """

        for edge in self.controledges:
            [source, target] = edge
            if not isinstance(source, node.ControlNode) and not isinstance(target, node.ControlNode):
                raise ValueError("All edges must be between control nodes")
        pass

    def run_graph(self, pointer, infograph, inputtank=None, transitionlimit=0):
        """
        Parameters
        ----------
        pointer: Control Node
            The node designated as the starting node for the interpretation of the MetaChem graph.
        infograph: Graph dictating information connections
        inputtank: Capability not currently implemented
            This container node is used to prime the system
        transitionlimit: int
            The number of node transitions for the system to perforom before exiting. This prevents the systems running
            infinitely

        Raises
        ------
        ValueError: "Pointer must be a control node"
            Raised if pointer is a container node rather than a control node
        """
        if pointer and not isinstance(pointer, node.ControlNode):
            raise ValueError("Pointer must be a control node")
        elif not isinstance(pointer, node.Termination):
            # input tank passed as variable to sload functions
            transitions = 0
            if inputtank:  # If loading from a file pass file into initial pointer for load function before main loop
                pointer.transition(infograph)
                pointer = self.graphdict[pointer]
            while transitions <= transitionlimit:
                if isinstance(pointer, node.Termination):
                    break
                elif isinstance(pointer, node.Decision):
                    # Different transfer protocol
                    # Find possible transitions then use transfer to get choice between them
                    options = self.graphdict[pointer]
                    choice = pointer.transition(infograph)
                    print([choice, options, type(pointer)]) if self.verbose else None
                    pointer = options[choice]  # Set new pointer
                elif isinstance(pointer, node.ControlNode):
                    # Transfer
                    pointer.transition(infograph)
                    pointer = self.graphdict[pointer]  # Find next pointer in graph and reset pointer
                if transitionlimit:
                    transitions = transitions+1
            # processes over the graph by running the nodes starting from the pointer with the preload files passed in


class Information(object):

    def __init__(self, edges):
        self.graphdict = {}
        edgetype = ['i', 'o', 'r']
        for edge in edges:
            self.check_info(edge)
            if edge[0] not in self.graphdict.keys():
                self.graphdict[edge[0]] = [None, None, None]
            t = edgetype.index(edge[2])
            try:
                self.graphdict[edge[0]][t] = self.graphdict[edge[0]][t] + edge[1]
            except:
                self.graphdict[edge[0]][t] = edge[1]

    @staticmethod
    def check_info(edge):
        if isinstance(edge[0], node.ControlNode) and isinstance(edge[1], node.ContainerNode):
            if isinstance(edge[0], node.Termination):
                raise TypeError("Terminination does not take input")
            elif edge[2] == "r":
                return None
            elif isinstance(edge[0], node.Decision):
                raise TypeError("Decision nodes can only read from containers")
            elif isinstance(edge[0], node.Observer):
                if not isinstance(edge[1], node.Environment):
                    raise TypeError("Observer can only read or write to environment containers")
            elif isinstance(edge[0], node.Action):
                if isinstance(edge[1], node.Tank):
                    raise TypeError("Actions can't read or write to Tank")
            elif isinstance(edge[0], node.Sampler):
                if isinstance(edge[1], node.Environment):
                    raise TypeError("Samplers can't read or write to Environments")
        else:
            raise TypeError("Information edge should be form: [ControlNode, ContainerNode, Type]")
