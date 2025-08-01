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

ConnmarkMatch
-------------

The :class:`ConnmarkMatch` class uses the same :ref:`mark_criterion` as
the :class:`MarkMatch` class.

Example::

    >>> from linuxnet.iptables import ConnmarkMatch
    >>> m = ConnmarkMatch()
    >>> m.mark().equals(0x10)
    <linuxnet.iptables.matches.connmarkmatch.ConnmarkMatch object at 0x7fa49c4acd60>
    >>> m.to_iptables_args()
    ['-m', 'connmark', '--mark', '0x10']


.. autoclass:: ConnmarkMatch
    :members:
    :inherited-members: Match

