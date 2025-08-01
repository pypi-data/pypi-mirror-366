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

MultiportMatch
--------------

The :class:`MultiportMatch` class provides access to the
**multiport** match extension.

Example::

    >>> from linuxnet.iptables import MultiportMatch
    >>> m = MultiportMatch()
    >>> m.source_ports().equals((80, 443, (8080,8089)))
    <linuxnet.iptables.matches.multiportmatch.MultiportMatch object at 0x7f4f773d4e20>
    >>> m.to_iptables_args()
    ['-m', 'multiport', '--source-ports', '80,443,8080:8089']

.. autoclass:: MultiportMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.multiportmatch

PortsCriterion
~~~~~~~~~~~~~~

.. autoclass:: PortsCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
