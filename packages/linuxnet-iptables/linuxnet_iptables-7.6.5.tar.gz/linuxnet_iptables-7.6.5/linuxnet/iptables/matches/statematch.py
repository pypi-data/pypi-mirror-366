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
This module provides matching against the connection tracking state
"""

from typing import Iterable

from ..deps import get_logger

from .match import Match, MatchParser
from .util import GenericCriterion

_logger = get_logger('linuxnet.iptables.matches.statematch')


class StateCriterion(GenericCriterion):
    """Compare with the connection tracking state

    The comparison value is a string.
    """
    def __init__(self, match: Match):
        super().__init__(match, '--state')


class StateMatch(Match):
    """Match against the connection tracking state

    This match is accessed via the **state** module, but it is not clear
    how its functionality is different from the **conntrack** module's
    --ctstate option.
    """
    def __init__(self):
        self.__state_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'state'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the state match criteria (only one).
        """
        return (self.__state_crit,)

    def state(self) -> StateCriterion:
        """Match against the connection tracking state
        """
        if self.__state_crit is None:
            self.__state_crit = StateCriterion(self)
        return self.__state_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Match against state::

            state RELATED,ESTABLISHED

        The 'state' field has already been consumed.

        :meta private:
        """
        criteria_iter = parser.get_iter()
        is_equal, val = parser.parse_value(next(criteria_iter))
        #
        # When negation is used, the behavior depends on the iptables version:
        #
        #   - iptables 1.4.7 computes the complement set and removes negation
        #   - iptables 1.8.4 uses negation
        #
        # The elimination of negation is problematic because the complement
        # set can be empty; this results in rules with a match list like this:
        #       state  state NEW
        #
        # We do not handle this scenario
        #
        if parser.get_negation() is not None:
            is_equal = False
        return StateMatch().state().compare(is_equal, val)


MatchParser.register_match('state', StateMatch)
