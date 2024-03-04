from metachem import CoreControl, CoreContainer, Simulate
from metachem.StringCatChem import stringcat_nodes
import networkx as nx

# Declare nodes.rst in graph.rst
graph = nx.DiGraph()

# containers
TTanks = CoreContainer.NestedGridTank(graph)
Vtime = CoreContainer.ListEnvironment(graph)
Vtime.add(0)
TTank = stringcat_nodes.StringCatTank(graph)
Scomposite = CoreContainer.ListSample(graph)
Vreactions = CoreContainer.ListEnvironment(graph)
Vreactions.add(0)
TLoad = CoreContainer.NestedGridTank(graph)  # Empty tank used as place holder as no input tank needed

# control nodes.rst
Sload = stringcat_nodes.StringCatLoadSampler(graph, TLoad, TTanks, size=100, tanks=400)
Otime = CoreControl.ClockObserver(graph, Vtime, Vtime)
Ssamplertank = CoreControl.SimpleSampler(graph, TTanks, TTank)
Ssamplerstring = CoreControl.SimpleSampler(graph, TTank, Scomposite)
Ssamplerstringdecomp = CoreControl.SimpleSampler(graph, TTank, Scomposite)
Ddecomp = stringcat_nodes.StringCatDecompDecision(graph, 2, Scomposite)
Aconcat = stringcat_nodes.StringCatConcatAction(graph, Scomposite, Scomposite)
Asplit = stringcat_nodes.StingCatSplitAction(graph, Scomposite, Scomposite)
Sreturn = CoreControl.BruteSampler(graph, Scomposite, TTank)
Scommit = stringcat_nodes.StringCatCommitSampler(graph, TTank, TTanks)
Oreaction = CoreControl.ClockObserver(graph, Vreactions, Vreactions)
Dupdate = CoreControl.CounterDecision(graph, 2, Vreactions, 200)
Stransfers = stringcat_nodes.StringCatTransfersSampler(graph, TTanks, TTanks, gridrows=20, gridcols=20, samplesize=1)

# Implement control edge set to get graph.rst
edges = [(Sload, Otime), (Otime, Ssamplertank), (Ssamplertank, Ssamplerstring), (Ssamplerstring, Ddecomp),
         (Ddecomp, Ssamplerstringdecomp), (Ddecomp, Asplit),   # Ddecomp splits control
         (Ssamplerstringdecomp, Aconcat),
         (Asplit, Sreturn), (Aconcat, Sreturn),  # Control merges again at Sreturn
         (Sreturn, Scommit), (Scommit, Oreaction), (Oreaction, Dupdate),  # Dupdate splits control again
         (Dupdate, Stransfers), (Dupdate, Ssamplertank),  # Loop to the start of reaction
         (Stransfers, Otime)]  # Loop to the start to the generation

for edge in edges:
    graph.add_edge(edge[0], edge[1])

system = Simulate.Simulate(graph, Sload)

# run graph.rst
system.run_graph(transition_limit=20000000)
print(TTanks.read())
# print(TTank.read())
# print(Scomposite.read())
