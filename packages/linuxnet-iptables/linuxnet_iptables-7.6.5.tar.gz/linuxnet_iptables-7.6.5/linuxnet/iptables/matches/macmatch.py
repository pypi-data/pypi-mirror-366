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
This module provides the MacMatch class which supports
matching against the MAC address
"""

from typing import Iterable

from ..deps import get_logger

from .match import Match, MatchParser
from .util import GenericCriterion

_logger = get_logger('linuxnet.iptables.matches.macmatch')


class MacSourceCriterion(GenericCriterion):
    """Compare with the MAC source address.

    The comparison value is an upper-case string
    """
    def __init__(self, match: Match):
        super().__init__(match, '--mac-source', norm=lambda s: s.upper())


class MacMatch(Match):
    """This class provides matching against the source MAC address
    """

    def __init__(self):
        self.__mac_source_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name.
        """
        return "mac"

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the packet match criteria; in this case, it is only
        the MAC source address criterion
        """
        return (self.__mac_source_crit,)

    def mac_source(self) -> MacSourceCriterion:
        """Match against the source address
        """
        if self.__mac_source_crit is None:
            self.__mac_source_crit = MacSourceCriterion(self)
        return self.__mac_source_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse the mark criteria::

            MAC 11:22:33:44:55:66
            MAC ! AA:22:33:44:55:66

        The 'MAC' field has already been consumed.

        :meta private:
        """
        is_equal, mac_addr = parser.parse_next_value()
        return MacMatch().mac_source().compare(is_equal, mac_addr)


MatchParser.register_match('MAC', MacMatch)
