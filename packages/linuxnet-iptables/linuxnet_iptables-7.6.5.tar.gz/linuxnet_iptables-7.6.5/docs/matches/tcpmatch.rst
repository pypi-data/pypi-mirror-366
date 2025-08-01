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

TcpMatch
--------

The :class:`TcpMatch` class provides access to the **tcp** match extension.
It supports the following **iptables(8)** options:
``--sport``, ``--dport``, ``--tcp-flags``, ``--sync``, ``--tcp-options``

Example::

    Type "help", "copyright", "credits" or "license" for more information.
    >>> from linuxnet.iptables import TcpMatch
    >>> m = TcpMatch()
    >>> m.dest_port().equals(22).syn().bit_set()
    <linuxnet.iptables.matches.tcpmatch.TcpMatch object at 0x7fa49c330dc0>
    >>> m.to_iptables_args()
    ['-m', 'tcp', '--syn', '--dport', '22']


.. autoclass:: TcpMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.tcpmatch

TcpFlagsCriterion
~~~~~~~~~~~~~~~~~

.. autoclass:: TcpFlagsCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

.. autoclass:: TcpFlag
    :class-doc-from: class
    :members:
    :member-order: bysource

-------

.. _source_port_criterion:

SourcePortCriterion
~~~~~~~~~~~~~~~~~~~

.. autoclass:: SourcePortCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

.. _dest_port_criterion:

DestPortCriterion
~~~~~~~~~~~~~~~~~

.. autoclass:: DestPortCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

TcpOptionCriterion
~~~~~~~~~~~~~~~~~~

.. autoclass:: TcpOptionCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
