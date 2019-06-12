import node
import numpy as np
# import container
# standard load/ gen node (2 versions, generic load and a generator node specific)
# Brute sampler pregen boids put into a list container.

# default ordered sampler

# uses first boid in sample (or random in unordered container) for reference to pull neighbours
class NeighbourSampler(node.Sampler):

    def __init__(self, containersin, containersout, readcontainers=None):
        super(NeighbourSampler, self).__init__(containersin, containersout, readcontainers)

    def read(self):
        self.boid = self.containersin[0].read()[0]
        self.Neighbours = [neighbour for neighbour in self.containersin[1].read() if neighbour.position[0] <= self.boid.position[0]+self.boid.R and neighbour.position[0] >= self.boid.position[0]-self.boid.R and neighbour.position[1] <= self.boid.position[1]+self.boid.R and neighbour.position[1] >= self.boid.position[1]-self.boid.R]

    def pull(self):
        self.containersin[1].remove(self.Neighbours)

    def push(self):
        self.containersout.add(self.Neighbours)

# BUILD Observer to generate averages of neighbours (check if this needs to include boid itself)
class NeighbourObserver(node.Observer):


    def __init__(self, containersin, containersout, readcontainers=None):
        super(NeighbourObserver, self).__init__(containersin, containersout, readcontainers)

    def read(self):
        self.boid = self.readcontainers[0].read()
        self.Neighbours = self.readcontainers[1].read()
        self.Oldav = self.containersin.read()


    def pull(self):
        self.containersout.remove(self.Oldav)

    def process(self):
        self.posAv = [np.mean([boid.currentposition[0] for boid in self.Neighbours]),np.mean([boid.currentposition[1] for boid in self.Neighbours])]
        self.volAv = [np.mean([boid.currentvelocity[0] for boid in self.Neighbours]),np.mean([boid.currentvelocity[1] for boid in self.Neighbours])]
        self.sepTot = sum(np.array([(self.boid.currentposition-n.currentposition)/(np.absolute(np.linalg.norm(self.boid.currentPosition-n.currentPosition))**2) for n in self. Neighbours]))

    def push(self):
        self.containersout.add([self.posAv, self.volAv, self.sepTot])

# BruteSampler to return neighbours

# flocking action and decision nodes COME BACK TO THESE

## decision for flock or wander
### Flock
#### a cohesion
#### align
#### seperation
#### whim
### random
#### random walk
## pacekeeping


# Ordered Sampler works with ordered containers, always adds to end and removes from start. Mostly done by using a type of ordered container.

# clock observer

# counter decision

# ordered sampler from above

# action update position and velocity

# ordered sampler from above

# clock observer

# counter decision

# observation logger - does all the things.



# Containers:
## sample input
## sample time 0
## smaple time 1
## tank n
## tank temp
## tank n+1
## sample boid
## tank neigh
##environment neigh

##### set update velocity in each boid and then update position afterwards