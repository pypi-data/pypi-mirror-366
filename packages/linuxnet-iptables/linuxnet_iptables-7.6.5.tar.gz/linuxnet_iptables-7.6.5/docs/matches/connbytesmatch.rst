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

ConnbytesMatch
--------------

Example::

    >>> from linuxnet.iptables import ConnbytesMatch
    >>> m = ConnbytesMatch()
    >>> m.mode().equals('packets').direction().equals('original').count().equals(100)
    <linuxnet.iptables.matches.connbytesmatch.ConnbytesMatch object at 0x7efe3a684b20>
    >>> m.to_iptables_args()
    ['-m', 'connbytes', '--connbytes', '100', '--connbytes-dir', 'original', '--connbytes-mode', 'packets']

.. autoclass:: ConnbytesMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

