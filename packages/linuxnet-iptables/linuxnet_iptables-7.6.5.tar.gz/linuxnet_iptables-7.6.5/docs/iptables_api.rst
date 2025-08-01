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

.. _iptables_api:

.. module:: linuxnet.iptables


linuxnet.iptables API
=====================

The **linuxnet.iptables** API provides the following classes:

* :class:`IptablesPacketFilterTable` : an object of this class
  contains :class:`Chain` objects
  representing the chains of the corresponding table
* :class:`Chain` : an object of this class contains :class:`ChainRule`
  objects representing the rules of the corresponding chain;
  the subclass :class:`BuiltinChain` provides additional methods
  to access the policy-related attributes of a builtin chain
* :class:`ChainRule` : objects of this class contain a
  list of ``Match`` objects and a ``Target`` object
* :ref:`Match <match>` subclasses to match against specific
  attributes of a packet
* :ref:`Target <target>` subclasses to provide access to the
  various **iptables(8)** targets

An :class:`IptablesPacketFilterTable` instance can be populated by reading
the current system configuration.
The :meth:`IptablesPacketFilterTable.read_system_config` method
invokes the **iptables** command and parses its output.
The :class:`Chain` objects it returns via its accessor methods
are *stable*: for a given chain name, the same :class:`Chain` object
will always be returned. This holds true until the next time
the :class:`IptablesPacketFilterTable`
is populated by reading the system configuration.

An :class:`IptablesPacketFilterTable` instance is either IPv4-specific or
IPv6-specific. When dealing with an :class:`IptablesPacketFilterTable`
instance, any IP addresses obtained and/or specified
(e.g. source/destination packet addresses used in filtering)
will be IPv4 addresses or IPv6 addresses depending on how
the instance was initialized.

A :class:`Chain` object keeps track of the
:class:`IptablesPacketFilterTable` that it belongs to.
This association is reset when
the :class:`IptablesPacketFilterTable`
is repopulated.

A :class:`ChainRule` object provides methods to construct **iptables(8)** rules.
The :class:`ChainRule` can then be inserted into a :class:`Chain`.
:class:`ChainRule` objects that are part of a :class:`Chain` are immutable.
They are also *stable*: the same objects will be returned by the
:class:`Chain` accessor methods.

:class:`ChainRule` objects that are part of a :class:`Chain` keep track
of their rule number. This number is updated as rules are inserted or
deleted from the :class:`Chain`.

The packet and byte count statistics that are part of every
:class:`Chain` and :class:`ChainRule` object are current as of the time of
reading the system configuration.

``Target`` objects can be compared to each other. Comparison is
by name; target arguments are not considered.

.. toctree::
   :maxdepth: 2
   :hidden:

   table
   chain
   rule
   match
   target
   exception
   extensibility
