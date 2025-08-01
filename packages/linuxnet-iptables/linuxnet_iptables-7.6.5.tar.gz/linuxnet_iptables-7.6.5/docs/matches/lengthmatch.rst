..
    Copyright (c) 2024, Panagiotis Tsirigotis
    
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

LengthMatch
--------------

Example::

    >>> from linuxnet.iptables import LengthMatch
    >>> m = LengthMatch()
    >>> m.length().equals(20,40)
    <linuxnet.iptables.matches.lengthmatch.LengthMatch object at 0x7efe3a7baf80>
    >>> m.to_iptables_args()
    ['-m', 'length', '--length', '20:40']

.. autoclass:: LengthMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

