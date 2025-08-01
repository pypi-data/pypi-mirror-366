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
This module provides matching against rate limits
"""

from typing import Iterable, List

from ..exceptions import IptablesError
from ..deps import get_logger

from .match import Match, Criterion, MatchParser
from .util import GenericCriterion
from .util import Rate as UtilRate

_logger = get_logger('linuxnet.iptables.matches.limitmatch')


class RateLimitCriterion(Criterion):
    """Compare with a rate limit

    The comparison value is a :class:`LimitMatch.Rate` object
    """

    def __init__(self, match: Match):
        super().__init__(match)
        self.__rate = None

    def get_value(self) -> 'LimitMatch.Rate':
        """Returns the value that the criterion is comparing against
        """
        return self.__rate

    def equals(self,                    # pylint: disable=arguments-differ
                rate: UtilRate) -> Match:
        """Compare with the specified rate (a :class:`LimitMatch.Rate`
        object)
        """
        self.__rate = rate
        return self._set_polarity(True)

    def not_equals(self, *args, **kwargs):
        """This :class:`Criterion` method is not supported because the
        limit match does not support '!'
        """
        raise IptablesError('method not_equals() not supported')

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified rate
        """
        return ['--limit', str(self.__rate)]


class BurstCriterion(GenericCriterion):
    """Compare with the burst limit

    The comparison value is an integer
    """
    def __init__(self, match: Match):
        super().__init__(match, '--limit-burst')

    def not_equals(self, *args, **kwargs):
        """This :class:`Criterion` method is not supported because the
        limit match does not support '!'
        """
        raise IptablesError('method not_equals() not supported')


class LimitMatch(Match):
    """Match against a rate limit with a maximum burst
    """

    # Make this available to users
    Rate = UtilRate

    def __init__(self):
        self.__rate_limit_crit = None
        self.__limit_burst_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'limit'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the limit match criteria: rate-limit, burst
        Note that the burst criterion will be ``None`` if the rate-limit
        criterion has not been set.
        """
        if (self.__rate_limit_crit is not None and
                        self.__rate_limit_crit.is_set()):
            burst_crit = self.__limit_burst_crit
        else:
            burst_crit = None
        return (self.__rate_limit_crit, burst_crit)

    def limit(self) -> RateLimitCriterion:
        """Compare with the rate limit
        """
        if self.__rate_limit_crit is None:
            self.__rate_limit_crit = RateLimitCriterion(self)
        return self.__rate_limit_crit

    def burst(self) -> BurstCriterion:
        """Compare with the burst limit
        """
        if self.__limit_burst_crit is None:
            self.__limit_burst_crit = BurstCriterion(self)
        return self.__limit_burst_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse limit match::

            limit: avg <num>/<interval> burst <num>

        The 'limit:' has already been consumed.

        :meta private:
        """
        parser.skip_field('avg')
        criteria_iter = parser.get_iter()
        match = LimitMatch()
        rate_spec = next(criteria_iter)
        match.limit().equals(cls.Rate.str2rate(rate_spec))
        parser.skip_field('burst')
        burst = int(next(criteria_iter))
        return match.burst().equals(burst)


MatchParser.register_match('limit:', LimitMatch)
