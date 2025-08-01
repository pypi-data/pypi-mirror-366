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

from typing import Iterable, List, Tuple

from ..deps import get_logger

from .match import Match, Criterion, MatchParser
from .util import BooleanCriterion

_logger = get_logger('linuxnet.iptables.matches.setmatch')


class MatchSetCriterion(Criterion):
    """Match against a set defined by **ipset(8)**
    """
    def __init__(self, match: Match):
        super().__init__(match)
        self.__name = None
        self.__flags = None

    def get_value(self) -> Tuple[str, str]:
        """The value is the tuple (set-name, flags)

        :rtype: tuple of ``(str, str)``
        """
        return (self.__name, self.__flags)

    def equals(self,                     # pylint: disable=arguments-differ
                name: str, flags: str) -> Match:
        """Check against the specified ipset name using the specified flags

        :param name: **ipset(8)** name
        :param flags: comma-separated list of **src** and/or **dst**
                specifications
        """
        self.__name = name
        self.__flags = flags
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified comparison
        """
        return ["--match-set", self.__name, self.__flags]


class _CounterCriterion(Criterion):
    """A criterion for a counter value comparison.
    """

    _EQ_COMP = '=='
    _LT_COMP = '<'
    _GT_COMP = '>'

    def __init__(self, match: Match, unit_name: str):
        super().__init__(match)
        self.__unit = unit_name
        self.__value = None
        self.__comp = None

    def get_value(self) -> Tuple[int, str]:
        """Returns the value that the criterion is comparing against
        and the comparison operation (as a string)

        :rtype: tuple of ``(int, str)``
        """
        return (self.__value, self.__comp)

    def equals(self, value: int) -> Match: # pylint: disable=arguments-differ
        """Check if the counter is equal to ``value``

        :param value: the counter value
        """
        self.__value = value
        self.__comp = self._EQ_COMP
        return self._set_polarity(True)

    def less_than(self, value: int) -> Match:
        """Check if the counter is less than ``value``

        :param value: the counter value
        """
        self.__value = value
        self.__comp = self._LT_COMP
        return self._set_polarity(True)

    def greater_than(self, value: int) -> Match:
        """Check if the counter is greater than ``value``

        :param value: the counter value
        """
        self.__value = value
        self.__comp = self._GT_COMP
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified comparison
        """
        if self.__comp == self._EQ_COMP:
            return [f"--{self.__unit}-eq", str(self.__value)]
        if self.__comp == self._LT_COMP:
            return [f"--{self.__unit}-lt", str(self.__value)]
        return [f"--{self.__unit}-gt", str(self.__value)]


class PacketCounterCriterion(_CounterCriterion):
    """A criterion for a packet counter value comparison used by
    :class:`SetMatch`.
    """
    def __init__(self, match: Match):
        super().__init__(match, "packets")


class ByteCounterCriterion(_CounterCriterion):
    """A criterion for a byte counter value comparison used by
    :class:`SetMatch`.
    """
    def __init__(self, match: Match):
        super().__init__(match, "bytes")


class SetMatch(Match):
    """Match against IP sets defined via **ipset(8)**
    """
    def __init__(self):
        self.__match_set_crit = None
        self.__return_nomatch_crit = None
        self.__update_counters_crit = None
        self.__update_subcounters_crit = None
        self.__packet_counter_crit = None
        self.__byte_counter_crit = None

    @staticmethod
    def get_match_name():
        """Returns the **iptables(8)** match extension name
        """
        return 'set'

    def get_criteria(self) -> Iterable[Criterion]:
        """Returns the set match criteria.
        """
        return (self.__match_set_crit, self.__return_nomatch_crit,
                self.__update_counters_crit, self.__update_subcounters_crit,
                self.__packet_counter_crit, self.__byte_counter_crit,)

    def match_set(self) -> MatchSetCriterion:
        """Returns the criterion to identify the IPset and flags
        """
        if self.__match_set_crit is None:
            self.__match_set_crit = MatchSetCriterion(self)
        return self.__match_set_crit

    def return_nomatch(self) -> BooleanCriterion:
        """Specify the ``--return-nomatch`` option.
        """
        if self.__return_nomatch_crit is None:
            self.__return_nomatch_crit = BooleanCriterion(self,
                                                "--return-nomatch",
                                                supports_negation=False)
        return self.__return_nomatch_crit

    def update_counters(self) -> BooleanCriterion:
        """Specify update of packet/byte counters
        """
        if self.__update_counters_crit is None:
            self.__update_counters_crit = BooleanCriterion(self,
                                                "--update-counters")
        return self.__update_counters_crit

    def update_subcounters(self) -> BooleanCriterion:
        """Specify update of packet/byte counters of the matching element
        in the member set of a list type
        """
        if self.__update_subcounters_crit is None:
            self.__update_subcounters_crit = BooleanCriterion(self,
                                                "--update-subcounters")
        return self.__update_subcounters_crit

    def packet_counter(self) -> PacketCounterCriterion:
        """Returns the criterion comparing against the set's packet counter
        """
        if self.__packet_counter_crit is None:
            self.__packet_counter_crit = PacketCounterCriterion(self)
        return self.__packet_counter_crit

    def byte_counter(self) -> ByteCounterCriterion:
        """Returns the criterion comparing against the set's byte counter
        """
        if self.__byte_counter_crit is None:
            self.__byte_counter_crit = ByteCounterCriterion(self)
        return self.__byte_counter_crit

    @classmethod
    def parse(cls,              # pylint: disable=too-many-branches
                parser: MatchParser) -> Match:
        """Possible output::

           match-set foo6 src,src,dst,dst,src,dst
           match-set foo6 dst,src return-nomatch
           match-set foo6 dst,src return-nomatch packets-eq 10
           match-set foo6 dst,src return-nomatch packets-eq 10 ! bytes-eq 512
           match-set foo6 dst,src ! update-counters
           ! match-set foo6 dst,src ! update-counters ! update-subcounters
           match-set foo6 dst,src return-nomatch packets-lt 10 bytes-gt 512

        :meta private:
        """
        criteria_iter = parser.get_iter()
        positive_match = parser.get_negation() is None
        match = SetMatch()
        set_name = next(criteria_iter)
        flags = next(criteria_iter)
        match.match_set().compare(positive_match, set_name, flags)
        for val in criteria_iter:
            positive_match = True
            if val == '!':
                positive_match = False
                val = next(criteria_iter)
            if val == 'return-nomatch':
                match.return_nomatch().equals()
            elif val == 'update-counters':
                match.update_counters().compare(positive_match)
            elif val == 'update-subcounters':
                match.update_subcounters().compare(positive_match)
            elif val == 'packets-eq':
                match.packet_counter().compare(positive_match,
                                        int(next(criteria_iter)))
            elif val == 'packets-lt':
                match.packet_counter().less_than(int(next(criteria_iter)))
            elif val == 'packets-gt':
                match.packet_counter().greater_than(int(next(criteria_iter)))
            elif val == 'bytes-eq':
                match.byte_counter().compare(positive_match,
                                        int(next(criteria_iter)))
            elif val == 'bytes-lt':
                match.byte_counter().less_than(int(next(criteria_iter)))
            elif val == 'bytes-gt':
                match.byte_counter().greater_than(int(next(criteria_iter)))
            else:
                criteria_iter.put_back(val)
                if not positive_match:
                    criteria_iter.rewind()
                break
        return match

MatchParser.register_match('match-set', SetMatch)
