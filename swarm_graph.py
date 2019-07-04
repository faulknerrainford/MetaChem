import swarm_nodes
import swarm_particles
import container
import control
import node
import graph

gen_num = 10
bounds = [-1000, 1000, -1000, 1000]
boid_size = 1
swarm_size = 300
ani_steps = 5

# Containers:
#   sample input
samplein = container.ListSample()
samplein.add(swarm_particles.initialise_swarm([[132, [45.91, 10.82, 21.11, 0.86, 0.13, 42.48, 0.32, 0.74]],
                                               [84, [113.26, 3.41, 25.71, 0.4, 0.39, 49.53, 0.13, 0.24]]], bounds,
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
ocol = swarm_nodes.CollisionObserver(envColl, envColl, tankn)
scol = swarm_nodes.CollisionSampler(tankn, samplecol, envColl)
acol = swarm_nodes.CollisionAction([samplecol, envColl], samplecol)
srcol = control.BruteSampler(samplecol, tankn)
demptyc = control.EmptyDecision(2, envColl)
# Terminator, decision and visualiser
dgen = control.CounterDecision(2, envGen, gen_num)  # Termination as option 2
oviz = swarm_nodes.VisualizerObserver(envPos, bounds, boid_size, gen_num, ani_steps, 'Swarm_Animation.mp4')
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
