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

CommentMatch
------------

Example::

    >>> from linuxnet.iptables import CommentMatch
    >>> m = CommentMatch()
    >>> m.comment().equals("some random text")
    <linuxnet.iptables.matches.commentmatch.CommentMatch object at 0x7f6adbe86208>
    >>> m.to_iptables_args()
    ['-m', 'comment', '--comment', 'some random text']


.. autoclass:: CommentMatch
    :members:
    :inherited-members: Match
    :member-order: bysource

-------

.. currentmodule:: linuxnet.iptables.matches.commentmatch

CommentCriterion
~~~~~~~~~~~~~~~~

.. autoclass:: CommentCriterion
    :class-doc-from: class
    :inherited-members:
    :member-order: bysource
