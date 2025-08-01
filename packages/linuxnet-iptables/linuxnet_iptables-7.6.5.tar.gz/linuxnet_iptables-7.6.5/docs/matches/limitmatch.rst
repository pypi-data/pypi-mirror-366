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

-------

LimitMatch
----------

Example:

    >>> from linuxnet.iptables import LimitMatch 
    >>> m = LimitMatch()
    >>> m.limit().equals(LimitMatch.Rate(1)).burst().equals(10) 
    <linuxnet.iptables.matches.limitmatch.LimitMatch object at 0x7f4191c70208>
    >>> m.to_iptables_args()
    ['-m', 'limit', '--limit', '1/sec', '--limit-burst', '10']
    >>> m = LimitMatch()
    >>> Rate = LimitMatch.Rate
    >>> m.limit().equals(Rate(3, Rate.PER_MINUTE))
    <linuxnet.iptables.matches.limitmatch.LimitMatch object at 0x7f4191c704e0>
    >>> m.to_iptables_args()
    ['-m', 'limit', '--limit', '3/min']

.. autoclass:: LimitMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.limitmatch

RateLimitCriterion
~~~~~~~~~~~~~~~~~~

.. autoclass:: RateLimitCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

BurstCriterion
~~~~~~~~~~~~~~

.. autoclass:: BurstCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

