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
This module provides matching against ICMP attributes
"""

from typing import Iterable, List, Optional, Tuple

from ..exceptions import IptablesError, IptablesParsingError
from ..deps import get_logger

from .match import Match, Criterion, MatchParser


_logger = get_logger('linuxnet.iptables.matches,icmpmatch')


class IcmpTypeCriterion(Criterion):
    """Compare with the ICMP type.

    The comparison value is the tuple
    (icmp-type-name, icmp-type-value, icmp-code); icmp-type-name
    is a string, icmp-type-value is an integer, and icmp-code is an integer.
    icmp-type-name and icmp-code may be ``None``.

    See **iptables(8)** for a list valid icmp-type-name values.
    """

    # Mapping of ICMP codes to iptables(8) --icmp-type parameter values
    __VAL2NAME_MAP = {
                    (-1, None) : 'any',
                    (0, None)  : 'echo-reply',
                    (3, None)  : 'destination-unreachable',
                    (3, 0)     : 'network-unreachable',
                    (3, 1)     : 'host-unreachable',
                    (3, 2)     : 'protocol-unreachable',
                    (3, 3)     : 'fragmentation-needed',
                    (3, 5)     : 'source-route-failed',
                    (3, 6)     : 'network-unknown',
                    (3, 7)     : 'host-unknown',
                    # (3, 8) not provided
                    (3, 9)     : 'network-prohibited',
                    (3, 10)    : 'host-prohibited',
                    (3, 11)    : 'TOS-network-unreachable',
                    (3, 12)    : 'TOS-host-unreachable',
                    (3, 13)    : 'communication-prohibited',
                    (3, 14)    : 'host-precedence-violation',
                    (3, 15)    : 'precedence-cutoff',
                    (4, None)  : 'source-quench',
                    (5, None)  : 'redirect',
                    (5, 0)     : 'network-redirect',
                    (5, 1)     : 'host-redirect',
                    (5, 2)     : 'TOS-network-redirect',
                    (5, 3)     : 'TOS-host-redirect',
                    (8, None)  : 'echo-request',
                    (9, 0)     : 'router-advertisement',
                    (10, None) : 'router-solicitation',
                    (11, None) : 'time-exceeded',
                    (11, 1)    : 'ttl-zero-during-transit',
                    (11, 2)    : 'ttl-zero-during-reassembly',
                    (12, None) : 'parameter-problem',
                    (12, 0)    : 'ip-header-bad',
                    (12, 1)    : 'required-option-missing',
                    (13, None) : 'timestamp-request',
                    (14, None) : 'timestamp-reply',
                    (17, None) : 'address-mask-request',
                    (18, None) : 'address-mask-reply',
                }
    __NAME2VAL_MAP = {v : k for k, v in __VAL2NAME_MAP.items()}

    def __init__(self, match: Match):
        super().__init__(match)
        # If __icmp_type_name is not None, __icmp_type_value and __icmp_code
        # must be None.
        # If icmp_type_value is not None, __icmp_code may or may not be None
        self.__icmp_type_name = None
        self.__icmp_type_value = None
        self.__icmp_code = None

    def get_type_name(self) -> Optional[str]:
        """Returns the ICMP type name
        """
        return self.__icmp_type_name

    def get_type_value(self) -> int:
        """Returns the ICMP type value
        """
        return self.__icmp_type_value

    def get_code(self) -> Optional[int]:
        """Returns the ICMP code
        """
        return self.__icmp_code

    def get_value(self) -> Tuple[Optional[str], int, Optional[int]]:
        """Returns the value that the criterion is comparing against.
        This is a tuple :code:`(icmp_type_name, icmp_type_value, icmp_code)`;
        :code:`icmp_type_value` is an integer.
        :code:`icmp_type_name` is a string and may be ``None``.
        :code:`icmp_code` is an integer and may be ``None``.
        """
        return (self.__icmp_type_name, self.__icmp_type_value, self.__icmp_code)

    def equals(self,                    # pylint: disable=arguments-differ)
                        icmp_type_name: Optional[str] =None,
                        icmp_type_value: Optional[int] =None,
                        icmp_code: Optional[int] =None) -> Match:
        """Check for equality against the specified ICMP type name or value;
        one of the two must be present.

        :param icmp_type_name: a string from one of the values
            accepted by **iptables(8)**
        :param icmp_type_value: an integer specifiying the particular
            ICMP type value; the special value :code:`-1` maps to the
            type `any`.
        :param icmp_code: an optional integer specifying a particular code
            for the ICMP type; this parameter may be used with the
            :code:`icmp_type_value` parameter
        """
        if icmp_type_name is not None:
            if icmp_type_value is not None:
                raise IptablesError(
                        'cannot specify both ICMP type name and value')
            tc_tuple = self.__NAME2VAL_MAP.get(icmp_type_name)
            if tc_tuple is None:
                raise IptablesError(f'unknown ICMP type name: {icmp_type_name}')
            if icmp_code is not None and icmp_code != tc_tuple[1]:
                raise IptablesError(
                        f'specified ICMP code {icmp_code} does not match '
                        f'code {tc_tuple[1]} associated with type '
                        f'{icmp_type_name}')
            icmp_type_value, icmp_code = tc_tuple
        else:
            if icmp_type_value is None:
                raise IptablesError(
                        'must specify either ICMP type name or value')
            tc_tuple = (icmp_type_value, icmp_code)
            icmp_type_name = self.__VAL2NAME_MAP.get(tc_tuple)
        self.__icmp_type_name = icmp_type_name
        self.__icmp_type_value = icmp_type_value
        self.__icmp_code = icmp_code
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified mark

        We always use the ICMP type name in preference to the value/code
        combination.
        """
        retval = ['--icmp-type']
        if self.__icmp_type_name is not None:
            retval.append(self.__icmp_type_name)
        elif self.__icmp_type_value >= 0:
            val = f'{self.__icmp_type_value}'
            if self.__icmp_code is not None:
                val += f'/{self.__icmp_code}'
            retval.append(val)
        else:
            retval.append('any')
        return retval


class IcmpMatch(Match):
    """Match against the fields of the ICMP header
    """
    def __init__(self):
        self.__icmp_type_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'icmp'

    def get_criteria(self) -> Iterable[Criterion]:
        """Returns the ICMP match criteria (only one): icmp-type
        """
        return (self.__icmp_type_crit,)

    def icmp_type(self) -> IcmpTypeCriterion:
        """Criterion for matching against the ICMP type
        """
        if self.__icmp_type_crit is None:
            self.__icmp_type_crit = IcmpTypeCriterion(self)
        return self.__icmp_type_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse the ICMP criteria

        :meta private:
        """
        # iptables 1.4.7 output:
        #       icmp any
        #       icmp !any
        #       icmp type 3 [code <n>]
        #       icmp !type 3 [code <n>]
        # iptables 1.8.4 output:
        #       icmp any
        #       icmp !any
        #       icmptype 3 [code <n>]
        #       icmp !type 3 [code <n>]
        #
        # The icmp/icmptype has already been consumed.
        criteria_iter = parser.get_iter()
        match_name = parser.get_match_name()
        match = IcmpMatch()
        if match_name == 'icmp':
            is_equal, val = parser.parse_value(next(criteria_iter))
            if val == 'any':
                return match.icmp_type().compare(is_equal, icmp_type_name=val)
            if val != 'type':
                raise IptablesParsingError(f"unexpected value: {val}")
        elif match_name == 'icmptype':
            is_equal = True
        else:
            raise IptablesParsingError(f"ICMP unable to parse '{match_name}'")
        icmp_type_value = int(next(criteria_iter))
        if criteria_iter.peek() == 'code':
            _ = next(criteria_iter)
            icmp_code = int(next(criteria_iter))
        else:
            icmp_code = None
        return match.icmp_type().compare(is_equal,
                                icmp_type_value=icmp_type_value,
                                icmp_code=icmp_code)


MatchParser.register_match('icmp', IcmpMatch)
MatchParser.register_match('icmptype', IcmpMatch)
