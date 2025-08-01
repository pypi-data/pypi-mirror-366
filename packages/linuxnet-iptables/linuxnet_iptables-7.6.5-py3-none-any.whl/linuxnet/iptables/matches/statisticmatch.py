# Copyright (c) 2023, Panagiotis Tsirigotis

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
This module provides matching against IP sets defined by ipset(8)
"""

from typing import Iterable

from ..deps import get_logger

from .match import Match, Criterion, MatchParser
from .util import GenericCriterion, GenericPositiveCriterion

_logger = get_logger('linuxnet.iptables.matches.statisticmatch')


class StatisticMatch(Match):
    """Match packets based on some statistic condition
    """
    def __init__(self):
        self.__mode_crit = None
        self.__probability_crit = None
        self.__every_crit = None
        self.__packet_crit = None

    @staticmethod
    def get_match_name():
        """Returns the **iptables(8)** match extension name
        """
        return 'statistic'

    def get_criteria(self) -> Iterable[Criterion]:
        """Returns the set match criteria.
        """
        return (self.__mode_crit, self.__probability_crit,
                self.__every_crit, self.__packet_crit)

    def mode(self) -> GenericPositiveCriterion:
        """Returns the criterion that identifies the matching mode
        """
        if self.__mode_crit is None:
            self.__mode_crit = GenericPositiveCriterion(self, "--mode")
        return self.__mode_crit

    def probability(self) -> GenericCriterion:
        """Set the probability for ``random`` mode; the criterion value
        is a floating-point number.
        """
        if self.__probability_crit is None:
            self.__probability_crit = GenericCriterion(self, "--probability")
        return self.__probability_crit

    def every(self) -> GenericCriterion:
        """Identify the packet to match for the ``nth`` mode; the criterion
        value is an integer.
        """
        if self.__every_crit is None:
            self.__every_crit = GenericCriterion(self, "--every")
        return self.__every_crit

    def packet(self) -> GenericPositiveCriterion:
        """Set the initial counter value for the ``nth`` mode; the criterion
        value is an integer.
        """
        if self.__packet_crit is None:
            self.__packet_crit = GenericPositiveCriterion(self, "--packet")
        return self.__packet_crit

    @classmethod
    def parse(cls,              # pylint: disable=too-many-branches
                parser: MatchParser) -> Match:
        """Possible output::

            statistic mode random probability 0.50000000000
            statistic mode random ! probability 0.10000000009
            statistic mode nth every 100 packet 10
            statistic mode nth ! every 100 packet 10

        :meta private:
        """
        criteria_iter = parser.get_iter()
        parser.skip_field('mode')
        match = StatisticMatch()
        match.mode().equals(next(criteria_iter))
        for val in criteria_iter:
            positive_match = True
            if val == '!':
                positive_match = False
                val = next(criteria_iter)
            if val == 'probability':
                match.probability().compare(positive_match,
                                        float(next(criteria_iter)))
            elif val == 'every':
                match.every().compare(positive_match, int(next(criteria_iter)))
            elif val == 'packet':
                match.packet().compare(positive_match, int(next(criteria_iter)))
            else:
                criteria_iter.put_back(val)
                if not positive_match:
                    criteria_iter.rewind()
                break
        return match

MatchParser.register_match('statistic', StatisticMatch)
