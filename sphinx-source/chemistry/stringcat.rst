StringCat Chemistry
===================

StringCat Chemistry was developed as an illustrative example for MetaChem. Its atoms are the standard 26 lower case
characters of the English aplphabet. Composite particles are stings formed via concatenation. StringCat Chem is situated
in a collection of well-mixed (aspatial) tanks. When particles combine or split they remain
in the tank. When we select a string we check if it contains
any adjacent repeated letters; if so we split it between them.
If not we select a second string at random and concatenate
the two. We also randomly transfer strings between tanks.

The simplicity of this system means StringCatChem will
continue to run until everything has formed a small number of large particles in each tank, all with matching letters
at the starts and ends of them and no internal repeated letters. After this the system will not change. StringCatChem
is therefore not a good choice of AChem if one wishes to
study open-endedness or the transition to life. However, it
makes a good example of implementation: the whole system
can be implemented with 4 container nodes and 13 control
nodes.

.. image:: stringcatchem/SCC_implemented.png

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   stringcatchem/nodes