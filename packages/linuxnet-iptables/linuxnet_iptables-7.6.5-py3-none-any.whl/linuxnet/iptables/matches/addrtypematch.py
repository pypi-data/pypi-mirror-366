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
This module provides matching against the address type
"""

from typing import Iterable

from ..deps import get_logger

from .match import Match, MatchParser
from .util import GenericCriterion, BooleanCriterion

_logger = get_logger('linuxnet.iptables.matches.addrtype')


class AddressTypeMatch(Match):
    """Match against the address type
    """
    def __init__(self):
        self.__src_addr_type_crit = None
        self.__dst_addr_type_crit = None
        self.__limit_iface_in = None
        self.__limit_iface_out = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'addrtype'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the addrtype match criteria.
        """
        return (self.__src_addr_type_crit, self.__dst_addr_type_crit,
                        self.__limit_iface_in, self.__limit_iface_out)

    def src_addr_type(self) -> GenericCriterion:
        """Compare with the source address type.

        The comparison value is a string and should be one of the
        address type values listed in the documentation of the **addrtype**
        module in **iptables(8)**
        """
        if self.__src_addr_type_crit is None:
            self.__src_addr_type_crit = GenericCriterion(self, '--src-type')
        return self.__src_addr_type_crit

    def dst_addr_type(self) -> GenericCriterion:
        """Compare with the destination address type

        The comparison value is a string and should be one of the
        address type values listed in the documentation of the **addrtype**
        module in **iptables(8)**
        """
        if self.__dst_addr_type_crit is None:
            self.__dst_addr_type_crit = GenericCriterion(self, '--dst-type')
        return self.__dst_addr_type_crit

    def limit_iface_in(self) -> BooleanCriterion:
        """Address checking limited to the interface that the packet came from.

        This criterion does not support negation.
        Invocation of the :meth:`BooleanCriterion.not_equals` method
        will raise an :exc:`IptablesError`
        """
        if self.__limit_iface_in is None:
            self.__limit_iface_in = BooleanCriterion(self, '--limit-iface-in',
                                                supports_negation=False)
        return self.__limit_iface_in

    def limit_iface_out(self) -> BooleanCriterion:
        """Address checking limited to the interface that the packet
        is going out from.

        This criterion does not support negation.
        Invocation of the :meth:`BooleanCriterion.not_equals` method
        will raise an :exc:`IptablesError`
        """
        if self.__limit_iface_out is None:
            self.__limit_iface_out = BooleanCriterion(self, '--limit-iface-out',
                                                supports_negation=False)
        return self.__limit_iface_out

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse ADDRTYPE; the expected form is::

            ADDRTYPE match src-type UNICAST dst-type !UNICAST
            ADDRTYPE match src-type !BLACKHOLE dst-type !UNICAST limit-in
            ADDRTYPE match src-type MULTICAST limit-out
            ADDRTYPE match src-type PROHIBIT /* comment */

        The PKTTYPE field has already been consumed.

        :meta private:
        """
        parser.skip_field('match')
        criteria_iter = parser.get_iter()
        match = AddressTypeMatch()
        for val in criteria_iter:
            if val == 'src-type':
                eq_test, addr_type = parser.parse_value(next(criteria_iter))
                match.src_addr_type().compare(eq_test, addr_type)
            elif val == 'dst-type':
                eq_test, addr_type = parser.parse_value(next(criteria_iter))
                match.dst_addr_type().compare(eq_test, addr_type)
            elif val == 'limit-in':
                match.limit_iface_in().equals()
            elif val == 'limit-out':
                match.limit_iface_out().equals()
            else:
                # next match, or target
                criteria_iter.put_back(val)
                break
        return match

MatchParser.register_match('ADDRTYPE', AddressTypeMatch)
