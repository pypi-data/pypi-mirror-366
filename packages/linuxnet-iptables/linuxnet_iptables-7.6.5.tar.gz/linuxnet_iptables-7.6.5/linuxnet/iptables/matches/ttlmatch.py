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
This module provides matching against the packet TTL
"""

from typing import Iterable, List, Tuple

from ..exceptions import IptablesParsingError
from ..deps import get_logger

from .match import Match, Criterion, MatchParser, CriteriaExhaustedError

_logger = get_logger('linuxnet.iptables.matches.ttlmatch')


class TtlCriterion(Criterion):
    """A criterion for a TTL value comparison used by :class:`TtlMatch`.
    """

    _EQ_COMP = '=='
    _LT_COMP = '<'
    _GT_COMP = '>'

    def __init__(self, match: Match):
        super().__init__(match)
        self.__value = None
        self.__comp = None

    def get_value(self) -> Tuple[int, str]:
        """Returns the value that the criterion is comparing against
        and the comparison operation (as a string)

        :rtype: tuple of (int, str)
        """
        return (self.__value, self.__comp)

    def equals(self, value: int) -> Match: # pylint: disable=arguments-differ
        """Check if the packet TTL is equal to ``value``

        :param value: the TTL value
        """
        self.__value = value
        self.__comp = self._EQ_COMP
        return self._set_polarity(True)

    def less_than(self, value: int) -> Match:
        """Check if the packet TTL is less than ``value``

        :param value: the TTL value
        """
        self.__value = value
        self.__comp = self._LT_COMP
        return self._set_polarity(True)

    def greater_than(self, value: int) -> Match:
        """Check if the packet TTL is greater than ``value``

        :param value: the TTL value
        """
        self.__value = value
        self.__comp = self._GT_COMP
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified TTL comparison
        """
        if self.__comp == self._EQ_COMP:
            return ['--ttl-eq', str(self.__value)]
        if self.__comp == self._LT_COMP:
            return ['--ttl-lt', str(self.__value)]
        return ['--ttl-gt', str(self.__value)]


class TtlMatch(Match):
    """Match against the packet TTL value
    """
    def __init__(self):
        self.__ttl_crit = None

    @staticmethod
    def get_match_name():
        """Returns the **iptables(8)** match extension name
        """
        return 'ttl'

    def get_criteria(self) -> Iterable[Criterion]:
        """Returns the TTL match criteria (only one).
        """
        return (self.__ttl_crit,)

    def ttl(self) -> TtlCriterion:
        """Returns the TTL criterion
        """
        if self.__ttl_crit is None:
            self.__ttl_crit = TtlCriterion(self)
        return self.__ttl_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse the TTL criterion::

            TTL match TTL > 5

        :meta private:
        """
        criteria_iter = parser.get_iter()
        val = next(criteria_iter)
        if val != 'match':
            # It must be a TTL target
            criteria_iter.put_back(val)
            raise CriteriaExhaustedError()
        parser.skip_field('TTL')
        comp = next(criteria_iter)
        value = int(next(criteria_iter))
        if comp == '==':
            return TtlMatch().ttl().equals(value)
        if comp == '!=':
            return TtlMatch().ttl().not_equals(value)
        if comp == '>':
            return TtlMatch().ttl().greater_than(value)
        if comp == '<':
            return TtlMatch().ttl().less_than(value)
        raise IptablesParsingError(f"bad TTL comparison: '{comp}' ")

MatchParser.register_match('TTL', TtlMatch)
