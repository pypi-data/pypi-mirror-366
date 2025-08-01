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

IcmpMatch
---------

Example::

    >>> from linuxnet.iptables import IcmpMatch     
    >>> m = IcmpMatch()
    >>> m.icmp_type().equals('host-unreachable')
    <linuxnet.iptables.matches.icmpmatch.IcmpMatch object at 0x7fc9b5cab240>
    >>> m.to_iptables_args()
    ['-m', 'icmp', '--icmp-type', 'host-unreachable']
    >>> m1 = IcmpMatch()
    >>> m1.icmp_type().equals(icmp_type_value=3, icmp_code=1)
    <linuxnet.iptables.matches.icmpmatch.IcmpMatch object at 0x7fc9b5cab278>
    >>> m1.to_iptables_args()
    ['-m', 'icmp', '--icmp-type', 'host-unreachable']
    >>> m2 = IcmpMatch()
    >>> m2.icmp_type().equals(icmp_type_value=3, icmp_code=8)
    <linuxnet.iptables.matches.icmpmatch.IcmpMatch object at 0x7fc9b5cab550>
    >>> m2.to_iptables_args()
    ['-m', 'icmp', '--icmp-type', '3/8']


.. autoclass:: IcmpMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.icmpmatch

IcmpTypeCriterion
~~~~~~~~~~~~~~~~~

.. autoclass:: IcmpTypeCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
