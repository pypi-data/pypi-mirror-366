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

MacMatch
--------

Example::

    >>> from linuxnet.iptables import MacMatch
    >>> m = MacMatch()
    >>> m.mac_source().equals('12:34:56:78:9a:bc')
    <linuxnet.iptables.matches.macmatch.MacMatch object at 0x7fea123bc278>
    >>> m.to_iptables_args()
    ['-m', 'mac', '--mac-source', '12:34:56:78:9A:BC']


.. autoclass:: MacMatch
    :member-order: bysource
    :members:
    :inherited-members: Match

-------

.. currentmodule:: linuxnet.iptables.matches.macmatch

.. _mac_source_criterion:

MacSourceCriterion
~~~~~~~~~~~~~~~~~~

.. autoclass:: MacSourceCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:
