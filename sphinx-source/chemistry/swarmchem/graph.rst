######
Graph
######

The graph of Swarm Chemistry can be best described as a macro graph and the expansion of the flocking action as a second
graph.

The macro-level graph of our variant of SwarmChem is shown below. It operates as follows:

• **s**:Load Parameters: Starting node, which loads the initial parameter set from **T**:Parameters, and randomly positions the boids, stored in **S**:n.

• **o**:Generation: Iterate the clock. This “tick” is part of the discrete timing system that is consistent with all current swarm systems. This is evident in the rest of the macro system as well.

• **s**:Copy_to_Previous: The sampler copies the current generation from **S**:n to the tank **T**:n−1, which is used to hold the previous generation. This gives a copy of the previous state of all the boids for use in subsequent calculations.

• **a**:Flock: Update each boidʼs parameters (stored in **S**:n) by following the classic boid rules.

• **a**:Move: Move all the boids (stored in **S**:n) based on their parameters and current headings and velocities. This is common to all swarm chemistries.

• **o**:Collisions: Check for collisions, and record them in **V**:Collisions. This is part of our variant SwarmChem.

• **a**:Update_Params: Update parameter sets that are changed by collision. **S**:n now contains the fully updated generation.

• **s**:Log: Log the previous generation to **T**:external; clear **T**:n−1 ready for the current generation to be copied in the next loop iteration.

• Loop back for the next iteration.

.. image:: SwarmChemMacro.png

The Flocking action breaks down to a graph which is implemented in the code that goes through the processes of the
different aspects of flocking based on the observation of the boids neighbourhood.

.. image:: SwarmChemMicro.png

