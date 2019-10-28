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
Sload = stringcat_nodes.StringCatLoadSampler(size=100, tanks=400)
Otime = control.ClockObserver()
Ssamplertank = control.SimpleSampler()
Ssamplerstring = control.SimpleSampler()
Ssamplerstringdecomp = control.SimpleSampler()
Ddecomp = stringcat_nodes.StringCatDecompDecision(2)
Aconcat = stringcat_nodes.StringCatConcatAction()
Asplit = stringcat_nodes.StingCatSplitAction()
Sreturn = control.BruteSampler()
Scommit = stringcat_nodes.StringCatCommitSampler()
Oreaction = control.ClockObserver()
Dupdate = control.CounterDecision(2, 200)
Stransfers = stringcat_nodes.StringCatTransfersSampler(gridrows=20, gridcols=20, samplesize=1)

# Implement control edge set to get graph
edges = [[Sload, Otime], [Otime, Ssamplertank], [Ssamplertank, Ssamplerstring], [Ssamplerstring, Ddecomp],
         [Ddecomp, Ssamplerstringdecomp], [Ddecomp, Asplit],   # Ddecomp splits control
         [Ssamplerstringdecomp, Aconcat],
         [Asplit, Sreturn], [Aconcat, Sreturn],  # Control merges again at Sreturn
         [Sreturn, Scommit], [Scommit, Oreaction], [Oreaction, Dupdate],  # Dupdate splits control again
         [Dupdate, Stransfers], [Dupdate, Ssamplertank],  # Loop to the start of reaction
         [Stransfers, Otime]]  # Loop to the start to the generation

infoedges = [[Sload, TLoad, 'i'], [Sload, TTanks, 'o'], [Otime, Vtime, 'i'], [Otime, Vtime, 'o'],
             [Ssamplertank, TTanks,'i'], [Ssamplertank, TTank, 'o'], [Ssamplerstring, TTank, 'i'],
             [Ssamplerstring, Scomposite, 'o'], [Ssamplerstringdecomp, TTank, 'i'],
             [Ssamplerstringdecomp, Scomposite, 'o'], [Ddecomp, Scomposite, 'r'], [Aconcat, Scomposite, 'i'],
             [Aconcat, Scomposite, 'o'], [Asplit, Scomposite, 'i'], [Asplit, Scomposite, 'o'],
             [Sreturn, Scomposite, 'i'], [Sreturn, TTank, 'o'], [Scommit, TTank, 'i'], [Scommit, TTanks, 'o'],
             [Oreaction, Vreactions, 'i'], [Oreaction, Vreactions, 'o'], [Dupdate, Vreactions, 'r'],
             [Stransfers, TTanks, 'i'], [Stransfers, TTanks, 'o']]

info = graph.Information(infoedges)
system = graph.Graph(edges, verbose=True)

# run graph
system.run_graph(Sload, info, transitionlimit=200000)
print(TTanks.read())
print(TTank.read())
print(Scomposite.read())
