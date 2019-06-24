import swarm_nodes
import swarm_particles
import container
import control
import node
import graph

gen_num = 100
bounds = [-1000, 1000, -1000, 1000]
boid_size = 1
swarm_size = 100

# Containers:
#   sample input
samplein = container.ListSample()
samplein.add(swarm_particles.initialise_swarm([[1, [70.55, 5.52, 7.39, 0.97, 0.45, 35.51, 0.45, 0.06]]], bounds,
                                              swarm_size))
# fill start container

#   tank n
tankn = container.ListTank()
#   tank n+1
tankn1 = container.ListTank()
#   sample boid
tankt = container.ListTank()
sampleb = container.ListSample()
#   environment neigh
envAv = container.ListEnvironment()
#   Log environments
envPos = container.ListEnvironment()
envVel = container.ListEnvironment()
envGen = container.ListEnvironment()
envGen.add(0)
envNeigh = container.ListEnvironment()
envlog = container.ListEnvironment()

# Control nodes
sload = control.BruteSampler(samplein, tankn)
olog = swarm_nodes.VizLoggerObserver(envGen, [envlog, envPos, envVel, envGen], tankn)
sboid = control.SimpleSampler(tankn, sampleb)
oav = swarm_nodes.NeighbourObserver([envAv, envNeigh], [envAv, envNeigh], [sampleb, envPos, envVel])
dneigh = control.CounterDecision(2, envNeigh)  # Flocking as option 2
#   FLOCKING
arand = swarm_nodes.RWalkAction(sampleb, sampleb)
acoh = swarm_nodes.CohesionAction(sampleb, sampleb, envAv)
aali = swarm_nodes.AlignAction(sampleb, sampleb, envAv)
asep = swarm_nodes.SeperationAction(sampleb, sampleb, envAv)
awhi = swarm_nodes.WhimAction(sampleb, sampleb)
apac = swarm_nodes.UpdateVAction(sampleb, sampleb)
srboid = control.BruteSampler(sampleb, tankt)
demptyn = control.EmptyDecision(2, tankn)  # Loop as option 2
sboid1 = control.SimpleSampler(tankt, sampleb)
aupp = swarm_nodes.UpdatePAction(sampleb, sampleb)
srboid1 = control.BruteSampler(sampleb, tankn1)
demptyt = control.EmptyDecision(2, tankt)  # Loop as option 2
#   Generic decision based on if a tank or sample is empty
sreset = control.BruteSampler(tankn1, tankn)
# Terminator, decision and visualiser
dgen = control.CounterDecision(2, envGen, gen_num)  # Termination as option 2
oviz = swarm_nodes.VisualizerObserver(envPos, bounds, boid_size, gen_num)
term = node.Termination()

# Graph
swarm_edges = [[sload, olog], [olog, sboid], [sboid, oav], [oav, dneigh], [dneigh, arand], [dneigh, acoh],
               [acoh, aali], [aali, asep], [asep, awhi], [awhi, apac], [arand, apac],
               [apac, srboid], [srboid, demptyn], [demptyn, sboid1], [demptyn, sboid],
               [sboid1, aupp], [aupp, srboid1], [srboid1, demptyt], [demptyt, sreset], [demptyt, sboid1],
               [sreset, dgen], [dgen, olog], [dgen, oviz], [dgen, term]]

swarm_system = graph.Graph(swarm_edges, verbose=True)
swarm_system.run_graph(sload)
