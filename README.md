# MetaChem

This package implements the MetaChem frame work as described in [1]. The implementation is structured into four core modules: graph.py, node.py, control.py, container.py.

The graph.py module contains the graph class and it's key functions. This allows one to declare and run a MetaChem graph.

The node.py provides the node classes used in a MetaChem graph. These use abstract methods to insure the requirement for implementation of needed functions. These are just the core skeletons of the nodes.

The control.py and container.py modules provide implementations of nodes which have widely applicable functionality e.g. BruteSampler implements appending the entire content of one container to the end of another.

[1]. Rainford, Penelope Faulkner, Angelika Sebald, and Susan Stepney. 2019. “MetaChem: An Algebraic Framework for Artificial Chemistries.” arXiv [cs.ET]. arXiv. http://arxiv.org/abs/1905.12541.