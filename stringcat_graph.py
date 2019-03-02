import stringcat_nodes
import container
import control
import graph

# Declare nodes in graph

# containers
TTanks = container.ListTank()
Vtime = container.ListEnvironment()
Vtime.add(0)
TTank = stringcat_nodes.StringCatTank()
Scomposite = container.ListSample()
Vreactions = container.ListEnvironment()
Vreactions.add(0)
TLoad = container.ListTank()  # Empty tank used as place holder as no input tank needed

# control nodes
Sload = stringcat_nodes.StringCatLoadSampler(TLoad, TTanks, size=100, tanks=400)
Otime = control.ClockObserver(Vtime, Vtime)
Ssamplertank = control.SimpleSampler(TTanks, TTank)
Ssamplerstring = control.SimpleSampler(TTank, Scomposite)
Ssamplerstringdecomp = control.SimpleSampler(TTank, Scomposite)
Ddecomp = stringcat_nodes.StringCatDecompDecision(2, Scomposite)
Aconcat = stringcat_nodes.StringCatConcatAction(Scomposite, Scomposite)
Asplit = stringcat_nodes.StingCatSplitAction(Scomposite, Scomposite)
Sreturn = control.BruteSampler(Scomposite, TTank)
Scommit = stringcat_nodes.StringCatCommitSampler(TTank, TTanks)
Oreaction = control.ClockObserver(Vreactions, Vreactions)
Dupdate = control.CounterDecision(2, Vreactions, 200)
Stransfers = stringcat_nodes.StringCatTransfersSampler(TTanks, TTanks, gridrows=20, gridcols=20, samplesize=1)

# Implement control edge set to get graph
edges = [[Sload, Otime], [Otime, Ssamplertank], [Ssamplertank, Ssamplerstring], [Ssamplerstring, Ddecomp],
         [Ddecomp, Ssamplerstringdecomp], [Ddecomp, Asplit],   # Ddecomp splits control
         [Ssamplerstringdecomp, Aconcat],
         [Asplit, Sreturn], [Aconcat, Sreturn],  # Control merges again at Sreturn
         [Sreturn, Scommit], [Scommit, Oreaction], [Oreaction, Dupdate],  # Dupdate splits control again
         [Dupdate, Stransfers], [Dupdate, Ssamplertank],  # Loop to the start of reaction
         [Stransfers, Otime]]  # Loop to the start to the generation

system = graph.Graph(edges, verbose=True)

# run graph
system.run_graph(Sload, transitionlimit=200000)
print TTanks.read()
print TTank.read()
print Scomposite.read()
