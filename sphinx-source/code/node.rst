####
Node
####

Classes
=======
ContainerNode
^^^^^^^^^^^^^^
    Super class  for container nodes in MetaChem

.. autoclass:: node.ContainerNode
    :members:

ControlNode
^^^^^^^^^^^^
    Super class for control nodes in MetaChem

.. autoclass:: node.ControlNode
    :members:

Container Subclasses
=====================

Tank
^^^^^
    Container node which holds particles which can not be edited.

.. autoclass:: node.Tank
    :members:

Sample
^^^^^^^
    Container node which holds particles which can be edited.

.. autoclass:: node.Sample
    :members:

Environment
^^^^^^^^^^^^
    Container node which holds non-particle system and environment information.

.. autoclass:: node.Environment
    :members:


Control Subclasses
===================

Termination
^^^^^^^^^^^
    Node which indicated to the graph handler to stop running transitioning between nodes. This node has no outgoing
    control edge.

.. autoclass:: node.Termination
    :members:

Action
^^^^^^
    Node which modifies particles in a sample. It has a single outgoing control edge.

.. autoclass:: node.Action
    :members:

Decision
^^^^^^^^
    Node which branches control in the system. It has multiple outgoing control edges.

.. autoclass:: node.Decision
    :members:

Sampler
^^^^^^^
    Node which moves particles between tanks and samples.

.. autoclass:: node.Sampler
    :members:

Observer
^^^^^^^^
    Node which observes particles and environment and outputs information, sometimes summary statistics to the
    environment.

.. autoclass:: node.Observer
    :members:

