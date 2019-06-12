# standard load/ gen node (2 versions, generic load and a generator node specific)
# G - 2 BruteSamplers to put copies into tanks - generics should be usable
# G - default FirstSampler - generic - BUILD - takes first n elements in list container
# sampler build to read tank and sample to sample neighbours
# Observer for neighbour averages
# G - BruteSampler to return neighbours - generic
# subgraph
## decision for flock or wander - EmptyDecision - generic - BUILD
### Flock
#### Pull boid
#### a cohesion
#### align
#### seperation
#### whim
### random
#### random walk
## pacekeeping
## push boid - LastReturnSampler - returns samples to end of list tank and iterates an environment variable - not generic
## CounterDecision
## FirstSampler
## Action update position and velocity
## LastReturnSampler as above
## Counter Decision
## Observer Log

# Containers:
## env gen
## boids left (When editing keep it mod list length for double use. Possibly reset on decision. Or if <0 reset to len-1)
## sample input
## sample time 0
## smaple time 1
## tank n
## tank temp
## tank n+1
## sample boid
## tank neigh
## environment neigh
