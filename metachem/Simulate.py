"""
Graph module is designed to handle and run MetaChem graphs, see Rainford et. al. 2019. It currently only creates and
implements basic static MetaChem Graphs with all data preloaded and the information graph formed during control node
instantiation. Later efforts will modify control node class to allow node fuction to be declared and the information
links added separately. This will require the additional processing of the information links to be implemented in the
Graph object.

"""
from metachem import CoreNode


class Simulate(object):
    """
    A Class for describing and running MetaChem graphs. Capable of running Graph.

    Parameters
    -----------
    controledges : List<List(length =2)<node.ControlNode>>
        List of lists of control node pairs. This is the raw input control graph provided to the system, information
        graph is declared when instantiating control nodes. TO DO: Instantiate nodes based on an information
        graph input.
    verbose : Boolean
        Controls console output for debugging

    """

    def __init__(self, graph, start_node, verbose=False):
        self.graph = graph
        self.start_node = start_node
        self.graph_index = self.index_graph()
        self.verbose = verbose
        self.check_graph()

    def check_graph(self):
        """
        Function to check the input graph meets the specification of a MetaChem graph.

        Raises
        -------
        ValueError("Terminating control nodes must be Termination nodes")
            If the graph is incorrect a value error is raised to inform the user that the control graph is invalid
        """
        checked = []
        wait_list = []
        current = self.start_node
        while current not in checked:
            checked.append(current)
            check = self.graph.has_node(current)
            neighbour_list = list(self.graph.neighbors(current))
            neighbour_list = [x for x in neighbour_list if isinstance(x, CoreNode.ControlNode)]
            if not neighbour_list and not isinstance(current, CoreNode.Termination):
                raise Warning("May terminate incorrectly or have no termination node")
            wait_list = wait_list + neighbour_list
            wait_list = [x for x in wait_list if x not in checked]
            if wait_list:
                current = wait_list[0]
        return True

    def run_graph(self, transition_limit=0):
        """
        Manages the running of the graph starting at the given pointer and stopping at a termination node or after the
        processing of ControlNodes equal to the transition_limit.

        Parameters
        ----------
        transition_limit: int
            The number of node transitions for the system to perform before exiting. This prevents the systems running
            infinitely, even without a termination node.

        Raises
        ------
        ValueError: "Pointer must be a control node"
            Raised if pointer is a container node rather than a control node
        """
        if self.start_node and not isinstance(self.start_node, CoreNode.ControlNode):
            raise ValueError("Start must be a control node")
        elif not isinstance(self.start_node, CoreNode.Termination):
            # input tank passed as variable to sload functions
            transitions = 0
            pointer = self.start_node
            while transitions <= transition_limit:
                if isinstance(pointer, CoreNode.Termination):
                    break
                elif isinstance(pointer, CoreNode.Decision):
                    # Different transfer protocol
                    # Find possible transitions then use transfer to get choice between them
                    options = [x for x in list(self.graph.neighbors(pointer)) if isinstance(x, CoreNode.ControlNode)]
                    choice = pointer.transition()
                    print([choice, options, type(pointer)]) if self.verbose else None
                    pointer = options[choice]  # Set new pointer
                elif isinstance(pointer, CoreNode.ControlNode):
                    # Transfer
                    pointer.transition()
                    pointer = [x for x in list(self.graph.neighbors(pointer)) if isinstance(x, CoreNode.ControlNode)][0]  # Find next pointer in graph and reset pointer
                if transition_limit:
                    transitions = transitions+1
            # processes over the graph by running the nodes starting from the pointer with the preload files passed in

    def index_graph(self):
        return list(self.graph.nodes())

