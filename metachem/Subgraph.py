import networkx as nx


class Subgraph:

    def __init__(self, controls_in=1, controls_out=1, links=1):
        self.count_control_in = controls_in
        self.count_control_out = controls_out
        self.count_links = links
        self.graph = nx.DiGraph()
        self.links = []
        self.control_in = []
        self.control_out = []
