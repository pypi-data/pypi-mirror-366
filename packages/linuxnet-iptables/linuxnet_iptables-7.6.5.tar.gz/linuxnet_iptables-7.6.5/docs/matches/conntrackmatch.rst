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

ConntrackMatch
--------------

Example::

    >>> from linuxnet.iptables import ConntrackMatch
    >>> m = ConntrackMatch()
    >>> m.ctstate().equals('NEW')
    <linuxnet.iptables.matches.conntrackmatch.ConntrackMatch object at 0x7ffab737e208>
    >>> m.to_iptables_args()
    ['-m', 'conntrack', '--ctstate', 'NEW']


.. autoclass:: ConntrackMatch
    :member-order: bysource
    :members:
    :inherited-members: Match

-------

.. currentmodule:: linuxnet.iptables.matches.conntrackmatch

CtStateCriterion
~~~~~~~~~~~~~~~~

.. autoclass:: CtStateCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtStatusCriterion
~~~~~~~~~~~~~~~~~

.. autoclass:: CtStatusCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtDirectionCriterion
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: CtDirectionCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtOrigSrcCriterion
~~~~~~~~~~~~~~~~~~

.. autoclass:: CtOrigSrcCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtOrigDstCriterion
~~~~~~~~~~~~~~~~~~

.. autoclass:: CtOrigDstCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtReplSrcCriterion
~~~~~~~~~~~~~~~~~~

.. autoclass:: CtReplSrcCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtReplDstCriterion
~~~~~~~~~~~~~~~~~~

.. autoclass:: CtReplDstCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtOrigSrcPortCriterion
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: CtOrigSrcPortCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtOrigDstPortCriterion
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: CtOrigDstPortCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtReplSrcPortCriterion
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: CtReplSrcPortCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtReplDstPortCriterion
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: CtReplDstPortCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:

-------

CtExpireCriterion
~~~~~~~~~~~~~~~~~

.. autoclass:: CtExpireCriterion
    :class-doc-from: class
    :member-order: bysource
    :inherited-members:
