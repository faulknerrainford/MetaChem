from metachem import CoreContainer, CoreNode
from metachem.Subgraph import Subgraph
from metachem.StringCatChem.stringcat_nodes import StringCatDecompDecision, StringCatConcatAction, StingCatSplitAction


class SCCBond(Subgraph):

    def __init__(self):
        super(SCCBond, self).__init__(1, 1, 1)
        # Create link node
        slink = CoreContainer.LinkSample(self.graph)

        # Create control nodes
        ddecomp = StringCatDecompDecision(self.graph, 2, slink)
        aconcat = StringCatConcatAction(self.graph, slink, slink)
        adecomp = StingCatSplitAction(self.graph, slink, slink)
        anull = CoreNode.Action(self.graph, slink, slink)

        # Create edges and add to graph
        edges = [[ddecomp, aconcat], [ddecomp, adecomp], [aconcat, anull], [adecomp, anull]]
        for edge in edges:
            self.graph.add_edge(edge[0], edge[1])

        # Set up subgraph.
        self.links = [slink]
        self.control_in = [ddecomp]
        self.control_out = [anull]