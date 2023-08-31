############
Particles
############

The individuals in SwarmChem, often referred to as boids or agents, interact by each boid changing its own velocity
based on the local positions and velocities of its neighbors. This involves no knowledge of the neighborsʼ internal
parameters, just observation of their velocities and positions. This gives the effect of swarming or flocking like that
seen in birds. Different parameters sets produce swarms that differ in their density and in how they move. In SwarmChem
boids with different parameters are allowed to mix.

SwarmChem is a framework for a class of artificial chemistries. Its intention is to explore how higher-level statistical
rules for chemical systems emerge from lower-level local interactions. It does this with the basic concepts of Reynoldʼs
boids[1]. Flocking in both boids and SwarmChem works as follows: At each time step for each boid we first work out the
neighborhood of the boid. We then calculate an acceleration vector of the boid towards the center of the group of
neighboring boids; this is called the *cohesion*. We then calculate a vector toward the average heading of the
neighboring boids; this is called the *alignment*. We then calculate a vector to prevent crowding, moving to increase
the *separation* between boids. Finally we perform *pacekeeping*, which biases the pace (speed) of the boid towards its
normal speed in order to prevent all boidsʼ either becoming stationary or tending towards their maximum speeds. Then the
boid is moved, based on this information. This is done on all boids at once, so we use the information of position and
velocity from the current time step to calculate the next.

The main difference between Swarm Chemistry and Reynolds original swarms is that those were had a single parameter set
for the entire swarm while Swarm Chemistry allows for multiple parameter sets in the swarm.

[1] Reynolds, C. W. (1987). Flocks, herds and schools: A distributed behavioral model. In M. C. Stone (Ed.), Proceedings
of the 14th Annual Conference on Computer Graphics and Interactive Techniques, SIGGRAPH ʼ87 (pp. 25–34). New York:
ACM.

.. automodule:: source.SwarmChemistry.swarm_particles
    :members:
