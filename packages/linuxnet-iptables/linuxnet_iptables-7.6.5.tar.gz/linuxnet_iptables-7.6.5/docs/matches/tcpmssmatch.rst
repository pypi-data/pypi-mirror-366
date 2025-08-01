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

TcpmssMatch
-----------

Example::

    >>> from linuxnet.iptables import TcpmssMatch
    >>> m = TcpmssMatch()
    >>> m.mss().equals(500,600)
    <linuxnet.iptables.matches.tcpmssmatch.TcpmssMatch object at 0x7f4a19799240>
    >>> m.to_iptables_args()
    ['-m', 'tcpmss', '--mss', '500:600']


.. autoclass:: TcpmssMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.tcpmssmatch

MssCriterion
~~~~~~~~~~~~

.. autoclass:: MssCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
