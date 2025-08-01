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

StateMatch
----------

Example::

    >>> from linuxnet.iptables import StateMatch
    >>> m = StateMatch()
    >>> m.state().equals('NEW') is m
    True
    >>> m.to_iptables_args()
    ['-m', 'state', '--state', 'NEW']


.. autoclass:: StateMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.statematch

StateCriterion
~~~~~~~~~~~~~~

.. autoclass:: StateCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
