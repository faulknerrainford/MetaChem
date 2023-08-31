import abc

import networkx as nx


class Template:

    @abc.abstractmethod
    def __init__(self, bondgraph):
        self.bondgraph = bondgraph
        self.graph = nx.DiGraph()
        pass
