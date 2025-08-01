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

Chain
=====

The :class:`Chain` class provides access to a chain's rules with methods
to enumerate rules, find rules based on match and/or target,
create new rules, delete existing rules.
:class:`Chain` instances also provide access to the number of packets/bytes
that have traversed a chain by appropriately aggregating the
per-rule statistics provided by **iptables(8)**.

:class:`BuiltinChain` is a subclass of :class:`Chain` that additionally
provides access to the policy-related attributes of builtin chains.

---------------

.. autoclass:: Chain
    :members:
    :member-order: bysource

---------------

.. autoclass:: BuiltinChain
    :show-inheritance:
    :members:
    :member-order: bysource
