##########
Container
##########

A collection of ContainerNodes that implement standard functionality used across multiple AChems.


List Classes
=============
Containers which internally use lists for storage.

ListEnvironment
----------------

.. autoclass:: source.container.ListEnvironment
    :members:

ListSample
------------

.. autoclass:: source.container.ListSample
    :members:

ListTank
----------

.. autoclass:: source.container.ListTank
    :members:

Queue Classes
===============

Classes which use queues to store objects. This means all objects are added to the end of the queue and removable of
objects is done by removable from front. This means we only removing things from the front of the queue rather than
specific objects from within the queue.

QueueEnvironment
-----------------

.. autoclass:: source.container.QueueEnvironment
    :members:

QueueSample
-------------

.. autoclass:: source.container.QueueSample
    :members:

QueueTank
----------

.. autoclass:: source.container.QueueTank
    :members:

Stack Classes
===============

Classes which use stacks to store objects. This means all objects are added to the top of the stack and removable of
objects is done by removable from the top. This means we always start by removing things from the top of the stack
rather than specific objects from within the stack.

StackEnvironment
-----------------

.. autoclass:: source.container.StackEnvironment
    :members:

StackSample
------------

.. autoclass:: source.container.StackSample
    :members:

StackTank
-----------

.. autoclass:: source.container.StackTank
    :members:

Dictionary Classes
===================

Classes which use dictionary's to store objects so all objects must have names and are stored in name, value, pairs.
Objects are also removed by name.

Dictionary Environment
-----------------------

.. autoclass:: source.container.DictionaryEnvironment
    :members:
