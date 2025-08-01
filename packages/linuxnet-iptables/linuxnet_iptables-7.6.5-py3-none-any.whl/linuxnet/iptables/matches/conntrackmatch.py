# Copyright (c) 2021, 2022, 2023, 2024, Panagiotis Tsirigotis

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
This module provides matching against connection tracking attributes
"""

from ipaddress import IPv4Network, IPv4Address, IPv6Network
from typing import Iterable, Optional, Tuple, Union

from ..exceptions import IptablesParsingError
from ..deps import get_logger

from .match import Match, MatchParser
from .packetmatch import ProtocolCriterion, AddressCriterion
from .util import (
                        GenericCriterion,
                        GenericPositiveCriterion,
                        NumberOrRangeCriterion,
                    )

_logger = get_logger('linuxnet.iptables.matches.conntrackmatch')


class CtStateCriterion(GenericCriterion):
    """Compare against the connection tracking state

    The comparison value is a string.
    """
    def __init__(self, match):
        super().__init__(match, '--ctstate')


class CtStatusCriterion(GenericCriterion):
    """Compare against the connection tracking status

    The comparison value is a string.
    """
    def __init__(self, match):
        super().__init__(match, '--ctstatus')


class CtDirectionCriterion(GenericPositiveCriterion):
    """Compare against the connection tracking direction

    The comparison value is a string.
    """
    def __init__(self, match):
        super().__init__(match, '--ctdir')


class CtOrigSrcCriterion(AddressCriterion):
    """Compare against the origin's source IP address.

    The comparison value is an :class:`IPv4Network` or an :class:`IPv6Network`
    """
    def __init__(self, match: Match, *, ipv6: Optional[bool] =None):
        super().__init__(match, '--ctorigsrc', ipv6)


class CtOrigDstCriterion(AddressCriterion):
    """Compare against the origin's destination IP address.

    The comparison value is an :class:`IPv4Network` or an :class:`IPv6Network`
    """
    def __init__(self, match: Match, *, ipv6: Optional[bool] =None):
        super().__init__(match, '--ctorigdst', ipv6)


class CtReplSrcCriterion(AddressCriterion):
    """Compare against the reply's source IP address.

    The comparison value is an :class:`IPv4Network` or an :class:`IPv6Network`
    """
    def __init__(self, match: Match, *, ipv6: Optional[bool] =None):
        super().__init__(match, '--ctreplsrc', ipv6)


class CtReplDstCriterion(AddressCriterion):
    """Compare against the reply's destination IP address.

    The comparison value is an :class:`IPv4Network` or an :class:`IPv6Network`
    """
    def __init__(self, match: Match, *, ipv6: Optional[bool] =None):
        super().__init__(match, '--ctrepldst', ipv6)


class CtOrigSrcPortCriterion(NumberOrRangeCriterion):
    """Compare against the origin's source port (or port range).

    The comparison value is the tuple (port, last_port) where
    last_port may be ``None``
    """
    def __init__(self, match: Match):
        super().__init__(match, '--ctorigsrcport', sep=':')


class CtOrigDstPortCriterion(NumberOrRangeCriterion):
    """Compare against the origin's destination port (or port range).

    The comparison value is the tuple (port, last_port) where
    last_port may be ``None``
    """
    def __init__(self, match: Match):
        super().__init__(match, '--ctorigdstport', sep=':')


class CtReplSrcPortCriterion(NumberOrRangeCriterion):
    """Compare against the reply's source port (or port range).

    The comparison value is the tuple (port, last_port) where
    last_port may be ``None``
    """
    def __init__(self, match: Match):
        super().__init__(match, '--ctreplsrcport', sep=':')


class CtReplDstPortCriterion(NumberOrRangeCriterion):
    """Compare against the origin's destination port (or port range).

    The comparison value is the tuple (port, last_port) where
    last_port may be ``None``
    """
    def __init__(self, match: Match):
        super().__init__(match, '--ctrepldstport', sep=':')


class CtExpireCriterion(NumberOrRangeCriterion):
    """Compare against the remaining lifetime of the connection tracking

    The comparison value is the tuple (time, end_time) where
    end_time may be ``None`` (time is measured in seconds)
    """
    def __init__(self, match: Match):
        super().__init__(match, '--ctexpire', sep=':')


class ConntrackMatch(Match):    # pylint: disable=too-many-instance-attributes
    """Match against the connection tracking attributes.
    """
    def __init__(self):
        self.__ctstate_crit = None
        self.__ctstatus_crit = None
        self.__ctdir_crit = None
        self.__ctproto_crit = None
        self.__ctorigsrc_crit = None
        self.__ctorigdst_crit = None
        self.__ctreplsrc_crit = None
        self.__ctrepldst_crit = None
        self.__ctorigsrcport_crit = None
        self.__ctorigdstport_crit = None
        self.__ctreplsrcport_crit = None
        self.__ctrepldstport_crit = None
        self.__ctexpire_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'conntrack'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the conntrack match criteria: ctstate, ctstatus
        """
        return (self.__ctstate_crit, self.__ctstatus_crit,
                self.__ctdir_crit, self.__ctproto_crit,
                self.__ctorigsrc_crit, self.__ctorigdst_crit,
                self.__ctreplsrc_crit, self.__ctrepldst_crit,
                self.__ctorigsrcport_crit, self.__ctorigdstport_crit,
                self.__ctreplsrcport_crit, self.__ctrepldstport_crit,
                self.__ctexpire_crit)

    def ctstate(self) -> CtStateCriterion:
        """Match against the connection tracking state
        """
        if self.__ctstate_crit is None:
            self.__ctstate_crit = CtStateCriterion(self)
        return self.__ctstate_crit

    def ctstatus(self) -> CtStatusCriterion:
        """Matching against the connection tracking status
        """
        if self.__ctstatus_crit is None:
            self.__ctstatus_crit = CtStatusCriterion(self)
        return self.__ctstatus_crit

    def ctdir(self) -> CtDirectionCriterion:
        """Matching against the connection tracking status
        """
        if self.__ctdir_crit is None:
            self.__ctdir_crit = CtDirectionCriterion(self)
        return self.__ctdir_crit

    def ctproto(self) -> ProtocolCriterion:
        """Matching against the L4 protocol
        """
        if self.__ctproto_crit is None:
            self.__ctproto_crit = ProtocolCriterion(self)
        return self.__ctproto_crit

    def ctorigsrc(self) -> CtOrigSrcCriterion:
        """Matching against the origin's source IP address
        """
        if self.__ctorigsrc_crit is None:
            self.__ctorigsrc_crit = CtOrigSrcCriterion(self)
        return self.__ctorigsrc_crit

    def ctorigdst(self) -> CtOrigDstCriterion:
        """Matching against the origin's destination IP address
        """
        if self.__ctorigdst_crit is None:
            self.__ctorigdst_crit = CtOrigDstCriterion(self)
        return self.__ctorigdst_crit

    def ctreplsrc(self) -> CtReplSrcCriterion:
        """Matching against the reply's source IP address
        """
        if self.__ctreplsrc_crit is None:
            self.__ctreplsrc_crit = CtReplSrcCriterion(self)
        return self.__ctreplsrc_crit

    def ctrepldst(self) -> CtReplDstCriterion:
        """Matching against the reply's destination IP address
        """
        if self.__ctrepldst_crit is None:
            self.__ctrepldst_crit = CtReplDstCriterion(self)
        return self.__ctrepldst_crit

    def ctorigsrcport(self) -> CtOrigSrcPortCriterion:
        """Matching against the origin's source port
        """
        if self.__ctorigsrcport_crit is None:
            self.__ctorigsrcport_crit = CtOrigSrcPortCriterion(self)
        return self.__ctorigsrcport_crit

    def ctorigdstport(self) -> CtOrigDstPortCriterion:
        """Matching against the origin's destination port
        """
        if self.__ctorigdstport_crit is None:
            self.__ctorigdstport_crit = CtOrigDstPortCriterion(self)
        return self.__ctorigdstport_crit

    def ctreplsrcport(self) -> CtReplSrcPortCriterion:
        """Matching against the replin's source port
        """
        if self.__ctreplsrcport_crit is None:
            self.__ctreplsrcport_crit = CtReplSrcPortCriterion(self)
        return self.__ctreplsrcport_crit

    def ctrepldstport(self) -> CtReplDstPortCriterion:
        """Matching against the replin's destination port
        """
        if self.__ctrepldstport_crit is None:
            self.__ctrepldstport_crit = CtReplDstPortCriterion(self)
        return self.__ctrepldstport_crit

    def ctexpire(self) -> CtExpireCriterion:
        """Matching against the replin's destination port
        """
        if self.__ctrepldstport_crit is None:
            self.__ctrepldstport_crit = CtReplDstPortCriterion(self)
        return self.__ctrepldstport_crit

    @staticmethod
    def __parse_addr(field: str) -> Union[IPv4Network, IPv6Network]:
        """Parse the address reported by iptables into an IPv4Network object.
        """
        if ':' in field:
            return IPv6Network(field)
        # Assume IPv4
        if '/' in field:
            return IPv4Network(field)
        #
        # Old iptables versions do not report the netmask, so we have to
        # guess it, e.g. 10.10.0.0 implies 10.10.0.0/16.
        # This is clearly ambiguous and we only detect /16, /24, and /28
        #
        addr = IPv4Address(field)
        num = (addr.packed[0] << 24 | addr.packed[1] << 16 |
                                addr.packed[2] << 8 | addr.packed[3])
        for prefix in (16, 24, 28):
            mask = (1 << (32-prefix)) - 1
            if (num & mask) == 0:
                field += f'/{prefix}'
                break
        return IPv4Network(field)

    @staticmethod
    def __parse_range(field: str) -> Tuple[int, Optional[int]]:
        """Parse a string of the form <num>[:<num] into a tuple
        """
        if ':' not in field:
            return (int(field), None)
        numfields = field.split(':')
        return (int(numfields[0]), int(numfields[1]))

    # pylint: disable=too-many-branches, too-many-statements
    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """The conntrack match is not identified by name in the iptables
        output. Instead, the parameters appear by themselves.
        The first parameter has already been consumed.

        :meta private:
        """
        criteria_iter = parser.get_iter()
        # Return the match_name and (optionally) negation to the iterator
        # so that we can process them as part of the for-loop below.
        # The for-loop is designed to handle all conntrack-related criteria
        # (which we expect to appear consecutively).
        # Because of the rewind, this method is now responsible for handling
        # StopIteration errors.
        parser.rewind_match()
        match = ConntrackMatch()
        criterion = None
        negation = None
        rewind = False
        #
        # The loop logic handles criteria that appear twice. This can happen
        # in the case of consecutive conntrack matches, e.g.
        #   iptables -m conntrack --ctstate NEW -m conntrack --ctstate INVALID
        #
        for token in criteria_iter:
            try:
                if token == '!':
                    negation = token
                    is_equal = False
                    criterion = next(criteria_iter)
                else:
                    is_equal = True
                    criterion = token
                if criterion == 'ctstate':
                    crit = match.ctstate()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, next(criteria_iter))
                elif criterion == 'ctstatus':
                    crit = match.ctstatus()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, next(criteria_iter))
                elif criterion == 'ctdir':
                    crit = match.ctdir()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, next(criteria_iter))
                elif criterion == 'ctproto':
                    crit = match.ctproto()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, next(criteria_iter))
                elif criterion == 'ctorigsrc':
                    crit = match.ctorigsrc()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, cls.__parse_addr(
                                                        next(criteria_iter)))
                elif criterion == 'ctorigdst':
                    crit = match.ctorigdst()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, cls.__parse_addr(
                                                        next(criteria_iter)))
                elif criterion == 'ctreplsrc':
                    crit = match.ctreplsrc()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, cls.__parse_addr(
                                                        next(criteria_iter)))
                elif criterion == 'ctrepldst':
                    crit = match.ctrepldst()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, cls.__parse_addr(
                                                        next(criteria_iter)))
                elif criterion == 'ctorigsrcport':
                    crit = match.ctorigsrcport()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, *cls.__parse_range(
                                                        next(criteria_iter)))
                elif criterion == 'ctorigdstport':
                    crit = match.ctorigdstport()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, *cls.__parse_range(
                                                        next(criteria_iter)))
                elif criterion == 'ctreplsrcport':
                    crit = match.ctreplsrcport()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, *cls.__parse_range(
                                                        next(criteria_iter)))
                elif criterion == 'ctrepldstport':
                    crit = match.ctrepldstport()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, *cls.__parse_range(
                                                        next(criteria_iter)))
                elif criterion == 'ctexpire':
                    crit = match.ctexpire()
                    if crit.is_set():
                        rewind = True
                        break
                    crit.compare(is_equal, *cls.__parse_range(
                                                        next(criteria_iter)))
                else:
                    rewind = True
                    break
                criterion = None
                negation = None
            except StopIteration as stopiter:
                if negation is not None or criterion is not None:
                    if criterion is None:
                        raise IptablesParsingError(
                                'negation without criterion') from stopiter
                    raise IptablesParsingError(
                                f'no value for {criterion}') from stopiter
        if rewind:
            criteria_iter.put_back(criterion)
            if negation is not None:
                criteria_iter.put_back(negation)
        return match
    # pylint: enable=too-many-branches, too-many-statements


MatchParser.register_match('ctstate', ConntrackMatch)
MatchParser.register_match('ctstatus', ConntrackMatch)
MatchParser.register_match('ctproto', ConntrackMatch)
MatchParser.register_match('ctorigsrc', ConntrackMatch)
MatchParser.register_match('ctorigdst', ConntrackMatch)
MatchParser.register_match('ctreplsrc', ConntrackMatch)
MatchParser.register_match('ctrepldst', ConntrackMatch)
MatchParser.register_match('ctorigsrcport', ConntrackMatch)
MatchParser.register_match('ctorigdstport', ConntrackMatch)
MatchParser.register_match('ctreplsrcport', ConntrackMatch)
MatchParser.register_match('ctrepldstport', ConntrackMatch)
MatchParser.register_match('ctdir', ConntrackMatch)
MatchParser.register_match('ctexpire', ConntrackMatch)
