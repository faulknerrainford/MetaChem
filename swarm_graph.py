import swarm_nodes
import swarm_particles
import container
import control
# Containers:
#   sample input
samplein = container.ListSample()
# fill start container
samplein.add(swarm_particles.initialise_swarm([[1, [70.55, 5.52, 7.39, 0.97, 0.45, 35.51, 0.45, 0.06]]],
                                              [-1000, 1000, -1000, 1000], 100))

#   tank n
tankn = container.QueueTank()
#   tank n+1
tankn1 = container.ListTank()
#   sample boid
sampleb = container.ListSample()
#   environment neigh
envAv = container.ListEnvironment()
#   Log environments
envPos = container.ListEnvironment()
envVel = container.ListEnvironment()
envGen = container.ListEnvironment()

# Control nodes
sload = control.BruteSampler(samplein, tankn)
olog = swarm_nodes.VizLoggerObserver(None, [envPos, envVel, envGen], tankn)
sboid = control.SimpleSampler(tankn, sampleb)
oav = swarm_nodes.NeighbourObserver(envAv, envAv, [envPos, envVel])
#   FLOCKING
srboid = control.BruteSampler(sampleb, tankn1)
#   Generic decision based on if a tank or sample is empty
sreset = control.BruteSampler(tankn1, tankn)
# Terminator, decision and visualiser

# Graph
swarm_graph = {sload: olog}
