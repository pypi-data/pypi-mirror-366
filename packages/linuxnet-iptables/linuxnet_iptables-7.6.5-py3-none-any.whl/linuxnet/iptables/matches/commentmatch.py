# Copyright (c) 2021, 2022, 2023, Panagiotis Tsirigotis

# This file is part of linuxnet-iptables.
#
# linuxnet-iptables is free software: you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Affero General Public
# License as published by the Free Software Foundation.
#
# linuxnet-iptables is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General
# Public License along with linuxnet-iptables. If not, see
# <https://www.gnu.org/licenses/>.

"""
This module supports matching against comments
"""

from typing import Iterable

from ..exceptions import IptablesError
from ..deps import get_logger

from .match import Match, MatchParser
from .util import GenericCriterion

_logger = get_logger('linuxnet.iptables.matches.commentmatch')


class CommentCriterion(GenericCriterion):
    """Not really a criterion.

    The value is the comment string and is set
    using the :meth:`equals` method.
    """
    def __init__(self, match: Match):
        super().__init__(match, '--comment')

    def compare(self, is_equal: bool, *args, **kwargs) -> 'Match':
        """This :class:`Criterion` method is not supported
        """
        raise IptablesError('method compare() not supported')

    def not_equals(self, *args, **kwargs):
        """This :class:`Criterion` method is not supported
        """
        raise IptablesError('method not_equals() not supported')


class CommentMatch(Match):
    """Provide a way to add a comment to a rule
    """
    def __init__(self):
        self.__comment_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'comment'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the comment match criteria (only one).
        """
        return (self.__comment_crit,)

    def comment(self) -> CommentCriterion:
        """The rule comment
        """
        if self.__comment_crit is None:
            self.__comment_crit = CommentCriterion(self)
        return self.__comment_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse a comment. The comment has the form::

            /* some comment text */

        The leading '/*' has already been consumed when this method
        is called.

        :meta private:
        """
        criteria_iter = parser.get_iter()
        words = []
        for val in criteria_iter:
            if val == '*/':
                break
            words.append(val)
        return CommentMatch().comment().equals(' '.join(words))


MatchParser.register_match('/*', CommentMatch)
