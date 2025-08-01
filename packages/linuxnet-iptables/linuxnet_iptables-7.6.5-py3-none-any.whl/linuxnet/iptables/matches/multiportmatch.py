# Copyright (c) 2023, 2024, Panagiotis Tsirigotis

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
This module provides access to the multiport match extension
"""

from typing import Iterable, List

from ..exceptions import IptablesParsingError
from ..deps import get_logger

from .match import Criterion, Match, MatchParser

_logger = get_logger('linuxnet.iptables.matches.multiportmatch')


class PortsCriterion(Criterion):
    """Compare against a set of ports.

    The value is a tuple; each element of the tuple is either a port number,
    or a tuple indicating a port range, e.g. (80, 443, (1024, 65536))
    """
    def __init__(self, match: Match, iptables_option: str):
        super().__init__(match)
        self.__ports = set()
        self.__ranges = set()
        self.__option = iptables_option

    def get_value(self):
        """Returns the ports and ranges to compare against
        """
        ports = list(self.__ports)
        ports.sort()
        ranges = list(self.__ranges)
        ranges.sort()
        return tuple(ports + ranges)

    def equals(self, value: Iterable):  # pylint: disable=arguments-differ
        """Compare against a list of ports specified by ``value``
        """
        if len(value) == 0:
            raise ValueError("No value specified")
        for elem in value:
            if isinstance(elem, int):
                self.__ports.add(elem)
            else:
                # We expect something that supports indexing and has
                # a length of 2
                try:
                    if len(elem) != 2:
                        raise ValueError(f"Bad value: {elem}")
                    if not isinstance(elem[0], int):
                        raise ValueError(f"Not an integer: {elem[0]}")
                    if not isinstance(elem[1], int):
                        raise ValueError(f"Not an integer: {elem[1]}")
                    port_range = (elem[0], elem[1])
                    self.__ranges.add(port_range)
                except TypeError as typerr:       # does not support len()
                    raise ValueError(f"Bad value: {elem}") from typerr
                except IndexError as idxerr:
                    raise ValueError(f"Bad value: {elem}") from idxerr
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified ports
        """
        port_spec = []
        ports = list(self.__ports)
        ports.sort()
        for port in ports:
            port_spec.append(str(port))
        ranges = list(self.__ranges)
        ranges.sort()
        for port_range in ranges:
            port_spec.append(f"{port_range[0]}:{port_range[1]}")
        return [self.__option, ",".join(port_spec)]


class MultiportMatch(Match):
    """Match against sets of TCP/UDP ports.
    """

    def __init__(self):
        self.__source_ports_crit = None
        self.__dest_ports_crit = None
        self.__ports_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'multiport'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the multiport match criteria: source-ports,
        dest-ports, ports
        """
        return (self.__source_ports_crit, self.__dest_ports_crit,
                    self.__ports_crit)

    def source_ports(self) -> PortsCriterion:
        """Criterion with source ports to compare against
        """
        if self.__source_ports_crit is None:
            self.__source_ports_crit = PortsCriterion(self, '--source-ports')
        return self.__source_ports_crit

    def dest_ports(self) -> PortsCriterion:
        """Criterion with destination ports to compare against
        """
        if self.__dest_ports_crit is None:
            self.__dest_ports_crit = PortsCriterion(self, '--dest-ports')
        return self.__dest_ports_crit

    def ports(self) -> PortsCriterion:
        """Criterion with ports to compare against
        """
        if self.__ports_crit is None:
            self.__ports_crit = PortsCriterion(self, '--ports')
        return self.__ports_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse owner; the syntax is a concatenation of a subset of
        the following forms::

            multiport ports|sports|dports [!] port,port,port:port,...

        The leading 'multiport' field has already been consumed when
        this method is invoked.

        :meta private:
        """
        match = MultiportMatch()
        criteria_iter = parser.get_iter()
        token = next(criteria_iter)
        if token == 'ports':
            crit = match.ports()
        elif token == 'sports':
            crit = match.source_ports()
        elif token == 'dports':
            crit = match.dest_ports()
        else:
            raise IptablesParsingError(f"unexpected token: {token}")
        is_equal, port_list_spec = parser.parse_next_value()
        val_list = []
        for port_spec in port_list_spec.split(','):
            if ':' in port_spec:
                range_spec = port_spec.split(':', 1)
                port_range = (int(range_spec[0]), int(range_spec[1]))
                val_list.append(port_range)
            else:
                val_list.append(int(port_spec))
        return crit.compare(is_equal, val_list)


MatchParser.register_match('multiport', MultiportMatch)
