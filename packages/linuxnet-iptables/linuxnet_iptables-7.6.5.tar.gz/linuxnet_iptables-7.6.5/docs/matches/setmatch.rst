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

SetMatch
--------

Example::

    >>> from linuxnet.iptables import SetMatch
    >>> m = SetMatch()
    >>> m.match_set().equals('foo', 'src,dst')
    <linuxnet.iptables.matches.setmatch.SetMatch object at 0x7f886d7cf9a0>
    >>> m.to_iptables_args()
    ['-m', 'set', '--match-set', 'foo', 'src,dst']


.. autoclass:: SetMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.setmatch

MatchSetCriterion
~~~~~~~~~~~~~~~~~

.. autoclass:: MatchSetCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

PacketCounterCriterion
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: PacketCounterCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

ByteCounterCriterion
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ByteCounterCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
