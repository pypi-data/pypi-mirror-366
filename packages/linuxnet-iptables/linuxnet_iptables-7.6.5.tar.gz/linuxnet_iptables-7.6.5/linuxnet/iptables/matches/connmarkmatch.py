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
This module supports matching against the CT mark
"""

from typing import Iterable

from ..deps import get_logger

from .match import Match, MatchParser
from .markmatch import MarkCriterion

_logger = get_logger('linuxnet.iptables.matches.connmarkmatch')


class ConnmarkMatch(Match):
    """Match against the ctmark
    """
    def __init__(self):
        self.__mark_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'connmark'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the connmark match criteria (only one).
        """
        return (self.__mark_crit,)

    def mark(self) -> MarkCriterion:
        """Match against the packet's ctmark
        """
        if self.__mark_crit is None:
            self.__mark_crit = MarkCriterion(self)
        return self.__mark_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse the mark criteria::

            connmark match [!]<num>[/<num>]

        The 'connmark' field has already been consumed.

        :meta private:
        """
        parser.skip_field('match')
        is_equal, val = parser.parse_next_value()
        mask = None
        if '/' in val:
            valstr, maskstr = val.split('/', 1)
            value = int(valstr, 16)
            mask = int(maskstr, 16)
        else:
            value = int(val, 16)
        return ConnmarkMatch().mark().compare(is_equal, value, mask)


MatchParser.register_match('connmark', ConnmarkMatch)
