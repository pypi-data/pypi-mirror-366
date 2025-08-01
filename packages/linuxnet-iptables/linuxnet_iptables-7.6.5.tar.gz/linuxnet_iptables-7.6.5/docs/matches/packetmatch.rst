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

PacketMatch
-----------

Example::

    >>> m = PacketMatch()
    >>> m.input_interface().equals('eth0')
    <linuxnet.iptables.match.PacketMatch object at 0x7ff96e466e10>
    >>> m.fragment().not_equals()
    <linuxnet.iptables.match.PacketMatch object at 0x7ff96e466e10>
    >>> m.source_address().equals(IPv4Network('192.168.1.0/24'))
    <linuxnet.iptables.match.PacketMatch object at 0x7ff96e466e10>
    >>> m.to_iptables_args()
    ['-i', 'eth0', '!', '-f', '-s', '192.168.1.0/24']

.. autoclass:: PacketMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.packetmatch

InputInterfaceCriterion
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: InputInterfaceCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

OutputInterfaceCriterion
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: OutputInterfaceCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

ProtocolCriterion
~~~~~~~~~~~~~~~~~

.. autoclass:: ProtocolCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

SourceAddressCriterion
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: SourceAddressCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

DestAddressCriterion
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DestAddressCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

FragmentCriterion
~~~~~~~~~~~~~~~~~

.. autoclass:: FragmentCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
