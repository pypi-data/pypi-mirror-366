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

.. _match:

.. currentmodule:: linuxnet.iptables.extension

Matches
=======

The programmatic interface to packet matching is based on the concept
of a :class:`Match` object that provides methods returning
:class:`Criterion` objects which in turn allow for equality (and
inequality) testing against a stored value.

The various **iptables(8)** matches are provided by match-specific
subclasses of the :class:`Match` class, as shown in the example below.

-------

.. currentmodule:: linuxnet.iptables

:class:`PacketMatch` provides matching against packet attributes
such as protocol, source address, etc.

::

    m = PacketMatch()
    m.protocol().equals('udp')

The :meth:`protocol` method returns a
``ProtocolCriterion`` object which stores the value that
we want to compare against (``udp`` in this case).

A ``Match`` object may have multiple criteria; such criteria
are specific to the ``Match`` subclass.

Continuing the example::

    a = IPv4Network('1.2.3.4/32')
    mcast = IPV4Network('224.0.0.0/4')
    m.source_address().equals(a).dest_address().not_equals(mcast)

The :meth:`source_address` method returns a
``SourceAddressCriterion`` object, while
the :meth:`dest_address` method returns a
``DestAddressCriterion`` object.
The resulting ``Match`` object now matches ``UDP`` packets with
a source address of ``1.2.3.4`` and a destination address that is not
a multicast address.

-------

The following ``Match`` subclasses are available:

.. toctree::
    :maxdepth: 1
    :glob:

    matches/*
