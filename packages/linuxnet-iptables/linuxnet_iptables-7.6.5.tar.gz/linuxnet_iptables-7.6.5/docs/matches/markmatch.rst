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

MarkMatch
---------

Example::

    >>> from linuxnet.iptables import MarkMatch
    >>> m = MarkMatch()
    >>> m.mark().equals(0x20, 0xff)
    <linuxnet.iptables.matches.markmatch.MarkMatch object at 0x7f42fa72b240>
    >>> m.to_iptables_args()
    ['-m', 'mark', '--mark', '0x20/0xff']
    >>> m.mark().get_value()
    (32, 255)


.. autoclass:: MarkMatch
    :member-order: bysource
    :members:
    :inherited-members: Match

-------

.. currentmodule:: linuxnet.iptables.matches.markmatch

.. _mark_criterion:

MarkCriterion
~~~~~~~~~~~~~

.. autoclass:: MarkCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:
