..
    Copyright (c) 2023, Panagiotis Tsirigotis
    
    This file is part of linuxnet-iptables.
    
    linuxnet-iptables is free software: you can redistribute it and/or
    modify it under the terms of version 3 of the GNU Affero General Public
    License as published by the Free Software Foundation.
    
    linuxnet-iptables is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
    License for more details.
    
    You should have received a copy of the GNU Affero General
    Public License along with linuxnet-iptables. If not, see
    <https://www.gnu.org/licenses/>.

.. currentmodule:: linuxnet.iptables

-------

RecentMatch
-----------

The :class:`RecentMatch` class provides access to the **recent** match
extension. It supports the following **iptables(8)** options:
``--name``, ``--set``, ``--rsource``, ``--rdest``, ``--rcheck``,
``--update``, ``--remove``, ``--seconds``, ``--hitcount``, ``--rttl``.

Example:

>>> from linuxnet.iptables import RecentMatch
>>> m = RecentMatch()
>>> m.name().equals('badip').action().equals(RecentMatch.UPDATE).seconds().equals(60)
<linuxnet.iptables.matches.recentmatch.RecentMatch object at 0x7f2aa82212b0>
>>> m.to_iptables_args()
['-m', 'recent', '--update', '--name', 'badip', '--seconds', '60', '--rsource']

.. autoclass:: RecentMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.recentmatch


RecentMatchAction
~~~~~~~~~~~~~~~~~

.. autoclass:: RecentMatchAction
    :show-inheritance:
    :class-doc-from: class
    :members:
    :member-order: bysource


ActionCritetion
~~~~~~~~~~~~~~~

.. autoclass:: ActionCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

AddressSelection
~~~~~~~~~~~~~~~~

.. autoclass:: AddressSelection
    :show-inheritance:
    :class-doc-from: class
    :members:
    :member-order: bysource


AddressSelectionCriterion
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: AddressSelectionCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
