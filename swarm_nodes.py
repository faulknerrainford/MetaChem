import node
import numpy as np
# import container
# standard load/ gen node (2 versions, generic load and a generator node specific)
# action copy - possibly should be generic
# G - 2 bulk samplers to put copies into tanks - generics should be usable
# G - single sampler - generic
# sampler build to read tank and sample to sample neighbours
# Observer for neighbour averagess
# G - bulk sampler to return neighbours - generic
# subgraph
## decision for flock or wander
### Flock
#### a cohesion
#### align
#### seperation
#### whim
### random
#### random walk
## pacekeeping
## push boid
## loop
## pull each in tn+1 through sample into t temp
## update position while sample
## bulk transfer back to t:n+1.
## position update
# G - bulk return sammpler to put sample into next gen tank

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
