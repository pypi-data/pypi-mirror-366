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
This module provides matching against the packet type
"""

from typing import Iterable

from ..exceptions import IptablesParsingError
from ..deps import get_logger

from .match import Match, MatchParser
from .util import GenericCriterion

_logger = get_logger('linuxnet.iptables.matches.packettype')


class PacketTypeCriterion(GenericCriterion):
    """Compare with the packet type

    The comparison value is a string.
    """
    def __init__(self, match: Match):
        super().__init__(match, '--pkt-type')


class PacketTypeMatch(Match):
    """Match against the packet type
    """
    def __init__(self):
        self.__packet_type_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'pkttype'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the packet type match criteria (only one).
        """
        return (self.__packet_type_crit,)

    def packet_type(self) -> PacketTypeCriterion:
        """Compare with the packet type
        """
        if self.__packet_type_crit is None:
            self.__packet_type_crit = PacketTypeCriterion(self)
        return self.__packet_type_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse PKTTYPE; the expected form is::

            PKTTYPE op <packet-type>

        where op is '=' or '!='.
        The PKTTYPE field has already been consumed.

        :meta private:
        """
        criteria_iter = parser.get_iter()
        val = next(criteria_iter)
        if val == '=':
            is_equal = True
        elif val == '!=':
            is_equal = False
        else:
            _logger.error(
                "%s: parsing PKTTYPE: expected comparator; found '%s'",
                    cls.parse.__qualname__, val)
            raise IptablesParsingError("missing comparator field")
        return PacketTypeMatch().packet_type().compare(is_equal,
                                                        next(criteria_iter))


MatchParser.register_match('PKTTYPE', PacketTypeMatch)
