# Copyright (c) 2024, Panagiotis Tsirigotis

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
This module provides matching against the number of bytes/packets
of a connection
"""

from typing import Iterable

from ..deps import get_logger

from .match import Match, MatchParser
from .util import NumberOrRangeCriterion

_logger = get_logger('linuxnet.iptables.matches.lengthmatch')


class LengthMatch(Match):
    """Match against the length of the layer-3 payload
    """

    def __init__(self):
        self.__length_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'length'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the length match criteria: length
        """
        return (self.__length_crit,)

    def length(self) -> NumberOrRangeCriterion:
        """The length (or length range) we match against
        """
        if self.__length_crit is None:
            self.__length_crit = NumberOrRangeCriterion(self, '--length',
                                                        sep=':')
        return self.__length_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse the length match::

                length 10
                length !20
                length 30:100

        The leading 'length' field has already been consumed when this
        method is invoked.

        :meta private:
        """
        match = LengthMatch()
        is_equal, value = parser.parse_next_value()
        if ':' in value:
            fields = value.split(':', 1)
            from_val = int(fields[0])
            to_val = int(fields[1])
        else:
            from_val = int(value)
            to_val = None
        match.length().compare(is_equal, from_val, to_val)
        return match


MatchParser.register_match('length', LengthMatch)
