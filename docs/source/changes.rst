==========
Change log
==========


Version 1.0 Alpha 2 (unreleased)
================================

- Removed the :data:`booleano.nodes.OPERATIONS` constant because nodes must now
  extend the corresponding datatype.
- Placeholders are no longer operands. Now they are just nodes. They've been
  moved to :mod:`booleano.nodes.placeholders`.
- Functions are no longer operands. Now they are just nodes. The base class has
  been moved to :class:`booleano.nodes.Function`.
- The base class for developer defined variables,
  :class:`booleano.nodes.operands.classes.Variable`, is gone as well as
  the entire module. `Bug #569188
  <https://bugs.launchpad.net/booleano/+bug/569188>`_.
- Renamed :mod:`booleano.nodes.operands` to :mod:`booleano.nodes.constants`.

- Changed licensing terms:

  - Booleano is now available under the terms of the *GNU GPL Version 3* or
    later (it was the *MIT/X License*).
  - The logo is now licensed under the *Creative Commons Attribution-No
    Derivative Works 2.0 UK: England & Wales License* (it was the *Creative
    Commons Attribution-No Derivative Works 3.0 Spain License*).
  
  The documentation is still available under the Creative Commons
  Attribution-Share Alike 3.0 Unported License.


`Milestone on Launchpad <https://launchpad.net/booleano/+milestone/1.0a2>`_.


Version 1.0 Alpha 1 (2009-07-17)
================================

The first preview release of Booleano. All the essential functionality is
ready: the parser and the operations are completely implemented. Basic 
documentation is available.

This is a feature-incomplete release which is aimed at potential users in order
to get feedback about the shape they think Booleano should take. As a
consequence, the API may change drastically in future releases.

`Milestone on Launchpad <https://launchpad.net/booleano/+milestone/1.0a1>`_.
