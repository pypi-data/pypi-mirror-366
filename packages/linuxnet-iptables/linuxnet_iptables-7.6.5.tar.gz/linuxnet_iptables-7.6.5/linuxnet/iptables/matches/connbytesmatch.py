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
from .util import GenericPositiveCriterion, NumberOrRangeCriterion

_logger = get_logger('linuxnet.iptables.matches.connbytesmatch')


class ConnbytesMatch(Match):
    """Match against a connection's bytes or packets
    """

    def __init__(self):
        self.__count_crit = None
        self.__direction_crit = None
        self.__mode_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'connbytes'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the connbytes match criteria: count, direction, mode
        """
        return (self.__count_crit, self.__direction_crit, self.__mode_crit)

    def count(self) -> NumberOrRangeCriterion:
        """The bytes/packet count we match against
        """
        if self.__count_crit is None:
            self.__count_crit = NumberOrRangeCriterion(self, '--connbytes',
                                                        sep=':')
        return self.__count_crit

    def direction(self) -> GenericPositiveCriterion:
        """Flow direction
        """
        if self.__direction_crit is None:
            self.__direction_crit = GenericPositiveCriterion(self,
                                                        '--connbytes-dir')
        return self.__direction_crit

    def mode(self) -> GenericPositiveCriterion:
        """Flow mode
        """
        if self.__mode_crit is None:
            self.__mode_crit = GenericPositiveCriterion(self,
                                                        '--connbytes-mode')
        return self.__mode_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse the connbytes match::

            connbytes 1000 connbytes mode bytes connbytes direction original
            connbytes 1000:3000 connbytes mode packets connbytes direction reply
            connbytes 10:10000 connbytes mode avgpkt connbytes direction both
            ! connbytes 20:400 connbytes mode avgpkt connbytes direction both

        The leading 'connbytes' field (and the preceding '!' if present)
        has already been consumed when this method is invoked.

        :meta private:
        """
        match = ConnbytesMatch()
        criteria_iter = parser.get_iter()
        negation = parser.get_negation()
        value = next(criteria_iter)
        if ':' in value:
            fields = value.split(':', 1)
            from_val = int(fields[0])
            to_val = int(fields[1])
        else:
            from_val = int(value)
            to_val = None
        if negation is None:
            match.count().equals(from_val, to_val)
        else:
            match.count().not_equals(from_val, to_val)
        parser.skip_field('connbytes')
        parser.skip_field('mode')
        match.mode().equals(next(criteria_iter))
        parser.skip_field('connbytes')
        parser.skip_field('direction')
        match.direction().equals(next(criteria_iter))
        return match


MatchParser.register_match('connbytes', ConnbytesMatch)
