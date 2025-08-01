..
    Copyright (c) 2022, 2023, Panagiotis Tsirigotis
    
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

PacketTypeMatch
---------------

Example::

    >>> from linuxnet.iptables import PacketTypeMatch
    >>> m = PacketTypeMatch()
    >>> m.packet_type().equals('broadcast')
    <linuxnet.iptables.matches.packettypematch.PacketTypeMatch object at 0x7f1bee6ae240>
    >>> m.to_iptables_args()
    ['-m', 'pkttype', '--pkt-type', 'broadcast']
    >>> print(m.packet_type().get_value())
    broadcast

.. autoclass:: PacketTypeMatch
    :member-order: bysource
    :members:
    :inherited-members: Match

-------

.. currentmodule:: linuxnet.iptables.matches.packettypematch

PacketTypeCriterion
~~~~~~~~~~~~~~~~~~~

.. autoclass:: PacketTypeCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
