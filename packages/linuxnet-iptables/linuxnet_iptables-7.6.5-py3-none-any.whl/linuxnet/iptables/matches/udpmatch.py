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
This module supports matching against UDP packets
"""

from typing import Iterable

from ..deps import get_logger

from .match import Match, MatchParser
from .tcpmatch import _PortParser, SourcePortCriterion, DestPortCriterion

_logger = get_logger('linuxnet.iptables.matches.udpmatch')


class UdpMatch(Match):
    """Match against the source/destination UDP ports.
    """
    def __init__(self):
        self.__src_port_crit = None
        self.__dest_port_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'udp'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the UDP match criteria: source-port, dest-port
        """
        return (self.__src_port_crit, self.__dest_port_crit)

    def source_port(self) -> SourcePortCriterion:
        """Match against the source port
        """
        if self.__src_port_crit is None:
            self.__src_port_crit = SourcePortCriterion(self)
        return self.__src_port_crit

    def dest_port(self) -> DestPortCriterion:
        """Match against the destination port
        """
        if self.__dest_port_crit is None:
            self.__dest_port_crit = DestPortCriterion(self)
        return self.__dest_port_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse the UDP criteria::

            udp spts:!1:1024 dpt:53

        The 'udp' field has already been consumed.

        :meta private:
        """
        criteria_iter = parser.get_iter()
        match = UdpMatch()
        for val in criteria_iter:
            if val.startswith(_PortParser.PORT_PREFIX):
                _PortParser.parse(val, match)
            else:
                criteria_iter.put_back(val)
                break
        return match


MatchParser.register_match('udp', UdpMatch)
