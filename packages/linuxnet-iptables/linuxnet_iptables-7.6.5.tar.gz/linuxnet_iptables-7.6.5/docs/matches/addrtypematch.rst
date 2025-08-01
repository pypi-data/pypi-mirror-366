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

AddressTypeMatch
----------------

Example::

    >>> from linuxnet.iptables import AddressTypeMatch
    >>> m = AddressTypeMatch()
    >>> m.dst_addr_type().equals('BROADCAST').limit_iface_out().equals()
    <linuxnet.iptables.matches.addrtypematch.AddressTypeMatch object at 0x7fea365ca278>
    >>> m.to_iptables_args()
    ['-m', 'addrtype', '--dst-type', 'BROADCAST', '--limit-iface-out']
    >>> print(m.dst_addr_type().get_value())
    BROADCAST

.. autoclass:: AddressTypeMatch
    :member-order: bysource
    :members:
    :inherited-members: Match
