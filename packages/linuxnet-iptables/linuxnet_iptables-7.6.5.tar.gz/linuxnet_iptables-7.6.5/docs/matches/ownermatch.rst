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

OwnerMatch
-----------

Example::

    >>> from linuxnet.iptables import OwnerMatch
    >>> m = OwnerMatch()
    >>> m.uid().equals(10).gid().not_equals(100, 200).socket_exists()
    <linuxnet.iptables.matches.ownermatch.OwnerMatch object at 0x7f6adcd98240>
    >>> m.to_iptables_args()
    ['-m', 'owner', '--uid-owner', '10', '!', '--gid-owner', '100-200']
    >>> mm = OwnerMatch()
    >>> mm.socket_exists().equals()
    <linuxnet.iptables.matches.ownermatch.OwnerMatch object at 0x7f6adbe862b0>
    >>> mm.to_iptables_args()
    ['-m', 'owner', '--socket-exists']


.. autoclass:: OwnerMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.ownermatch

UidCriterion
~~~~~~~~~~~~

.. autoclass:: UidCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

GidCriterion
~~~~~~~~~~~~

.. autoclass:: GidCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

SocketExistsCriterion
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: SocketExistsCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource

-------

SupplGroupsCriterion
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: SupplGroupsCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
