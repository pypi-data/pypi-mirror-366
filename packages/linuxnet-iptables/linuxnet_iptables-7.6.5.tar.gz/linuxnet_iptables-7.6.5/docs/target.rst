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

.. _target:

.. currentmodule:: linuxnet.iptables.extension

Targets
=======

All target-related classes are derived from the :class:`Target` class.
The following subclasses are available:

.. currentmodule:: linuxnet.iptables

.. toctree::
    :maxdepth: 1
    :glob:

    targets/*

-------

The helper class :class:`Targets` provides access to the special 
targets (e.g. ``ACCEPT``).


.. autoclass:: Targets
    :members:
    :member-order: bysource

