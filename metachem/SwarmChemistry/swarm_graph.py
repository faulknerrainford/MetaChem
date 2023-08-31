from source.SwarmChemistry import swarm_nodes
from source.SwarmChemistry import swarm_particles
from source import control, container, node, graph

gen_num = 2000
bounds = [-1000, 1000, -1000, 1000]
boid_size = 1
swarm_size = 500
ani_steps = 3

# Containers:
#   sample input
samplein = container.ListSample()
samplein.add(swarm_particles.initialise_swarm([[102, [293.86, 17.06, 38.3, 0.81, 0.05, 0.83, 0.2, 0.9]],
                                               [124, [226.18, 19.27, 24.57, 0.95, 0.84, 13.09, 0.07, 0.8]],
                                               [74, [49.98, 8.44, 4.39, 0.92, 0.14, 96.92, 0.13, 0.51]]], bounds,
                                              swarm_size))
# fill start container

#   tank n
tankn = container.ListTank()
#   tank n+1
tankn1 = container.ListTank()
#   sample boid
tankt = container.ListTank()
sampleb = container.ListSample()
samplecol = container.ListSample()
#   environment neigh
envAv = container.ListEnvironment()
#   Log environments
envPos = container.ListEnvironment()
envVel = container.ListEnvironment()
envGen = container.ListEnvironment()
envGen.add(0)
envNeigh = container.ListEnvironment()
envlog = container.ListEnvironment()
envColl = container.StackEnvironment()

# Control Nodes
# Load parameters
sload = control.BruteSampler(samplein, tankn)
# Logging
olog = swarm_nodes.VizLoggerObserver(envGen, [envlog, envPos, envVel, envGen], tankn)
# Neighbourhood observation
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
# Update parameters after flocking
aupp = swarm_nodes.UpdatePAction(sampleb, sampleb, bounds)
srboid1 = control.BruteSampler(sampleb, tankn1)
demptyt = control.EmptyDecision(2, tankt)  # Loop as option 2
# Generic decision based on if a tank or sample is empty
sreset = control.BruteSampler(tankn1, tankn)
# Observe collisions
ocol = swarm_nodes.CollisionObserver(envColl, envColl, tankn)
scol = swarm_nodes.CollisionSampler(tankn, samplecol, envColl)
# Update parameters based on collision
acol = swarm_nodes.CollisionAction([samplecol, envColl], samplecol)
srcol = control.BruteSampler(samplecol, tankn)
demptyc = control.EmptyDecision(2, envColl)
# Terminator, decision and visualiser
dgen = control.CounterDecision(2, envGen, gen_num)  # Termination as option 2
oviz = swarm_nodes.VisualizerObserver(envPos, bounds, boid_size, gen_num, ani_steps, 'Swarm_Animation2.mp4')
term = node.Termination()

# Graph
swarm_edges = [[sload, olog], [olog, sboid], [sboid, oav], [oav, dneigh], [dneigh, arand], [dneigh, acoh],
               [acoh, aali], [aali, asep], [asep, awhi], [awhi, apac], [arand, apac],
               [apac, srboid], [srboid, demptyn], [demptyn, sboid1], [demptyn, sboid],
               [sboid1, aupp], [aupp, srboid1], [srboid1, demptyt], [demptyt, sreset], [demptyt, sboid1],
               [sreset, ocol], [ocol, demptyc], [demptyc, dgen], [demptyc, scol], [scol, acol], [acol, srcol],
               [srcol, demptyc], [dgen, olog], [dgen, oviz], [oviz, term]]

swarm_system = graph.Graph(swarm_edges, verbose=True)
swarm_system.run_graph(sload)
