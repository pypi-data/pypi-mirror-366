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

TtlMatch
--------

Example::

    >>> from linuxnet.iptables import TtlMatch
    >>> m = TtlMatch()
    >>> m.ttl().not_equals(32)
    <linuxnet.iptables.match.TtlMatch object at 0x7ff96e466f60>
    >>> m.to_iptables_args()
    ['-m', 'ttl', '!', '--ttl-eq', '32']
    >>> m = TtlMatch()
    >>> m.ttl().less_than(32)
    <linuxnet.iptables.match.TtlMatch object at 0x7ff96e466fd0>
    >>> m.to_iptables_args()
    ['-m', 'ttl', '--ttl-lt', '32']


.. autoclass:: TtlMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.ttlmatch

TtlCriterion
~~~~~~~~~~~~

.. autoclass:: TtlCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
