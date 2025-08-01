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

UdpMatch
--------

The :class:`UdpMatch` class uses the same
:ref:`source_port_criterion`
and 
:ref:`dest_port_criterion`
as the :class:`TcpMatch` class.

Example::

    >>> from linuxnet.iptables import UdpMatch
    >>> m = UdpMatch()
    >>> m.dest_port().equals(53)
    <linuxnet.iptables.match.UdpMatch object at 0x7ff96e466f98>
    >>> m.to_iptables_args()
    ['-m', 'udp', '--dport', '53']


.. autoclass:: UdpMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

