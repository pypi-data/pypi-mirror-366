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
This module supports matching against TCP packets
"""

from enum import IntFlag
from typing import Iterable, List, Optional, Set, Tuple

from ..exceptions import IptablesError, IptablesParsingError
from ..deps import get_logger

from .match import Match, Criterion, MatchParser
from .util import GenericCriterion, NumberOrRangeCriterion

_logger = get_logger('linuxnet.iptables.matches.tcpmatch')


class TcpFlag(IntFlag):
    """Names and values for the TCP flags.
    """
    #: ``FIN`` bit
    FIN = 0x1
    #: ``SYN`` bit
    SYN = 0x2
    #: ``RST`` bit
    RST = 0x4
    #: ``PSH`` bit
    PSH = 0x8
    #: ``ACK`` bit
    ACK = 0x10
    #: ``URG`` bit
    URG = 0x20


class TcpFlagsCriterion(Criterion):
    """A criterion for comparing against packets with an arbitrary set of
    TCP flags set, or for comparing against ``SYN`` packets. This is
    an either-or use, determined at the time of object instantiation.

    The value is the tuple (flags-checked, flags-set); both flags-checked
    and flags-set are comma-separated lists of TCP flag names as defined
    in :class:`TcpFlag`
    """
    def __init__(self, match: Match, syn_only=False):
        """
        :param match: the :class:`Match` object that owns this object
        :param syn_only: optional boolean value indicating a check only
            against the ``SYN`` flag
        """
        super().__init__(match)
        # If syn_only is True, then flags_checked/flags_set will be None
        self.__syn_only = syn_only
        self.__flags_checked = None
        self.__flags_set = None

    def __eq__(self, other):
        if not isinstance(other, TcpFlagsCriterion):
            return False
        if not self._may_be_equal(other):
            return False
        if self.is_syn_only() ^ other.is_syn_only():
            return self._any or other._any
        return self.get_value() == other.get_value()

    def get_value(self) -> Tuple[Set[TcpFlag], Set[TcpFlag]]:
        """Returns the value that the criterion is comparing against
        """
        return (self.__flags_checked, self.__flags_set)

    def is_syn_only(self) -> bool:
        """Returns ``True`` if the criterion is only meant to check
        for the SYN flag (but note that it may not be set yet)
        """
        return self.__syn_only

    def bit_set(self) -> Match:
        """This method can be used if this criterion implements a
        SYN-only comparison to check if the packet flags include only
        the SYN bit.
        """
        if not self.__syn_only:
            raise IptablesError('not a syn-only criterion')
        return self.equals()

    def bit_not_set(self) -> Match:
        """This method can be used if this criterion implements a
        SYN-only comparison to check for the non-existence of the SYN bit
        """
        return self.not_equals()

    def equals(self,            # pylint: disable=arguments-differ
                flags_checked: Optional[Set[TcpFlag]] =None,
                flags_set: Optional[List[TcpFlag]] =None) -> Match:
        """Perform flags comparison
        """
        if self.__syn_only:
            if not (flags_checked is None and flags_set is None):
                raise IptablesError("cannot set flags in SYN criterion")
            return self._set_polarity(True)
        if flags_checked is None:
            raise IptablesError("need to specify flags to check")
        if flags_set is None:
            raise IptablesError("need to specify flags that are set")
        self.__flags_checked = frozenset(flags_checked)
        self.__flags_set = frozenset(flags_set)
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified TCP flags
        """
        if self.__syn_only:
            return ['--syn']
        return ['--tcp-flags',
                ','.join([f.name for f in self.__flags_checked]),
                ','.join([f.name for f in self.__flags_set])]


class SourcePortCriterion(NumberOrRangeCriterion):
    """Compare with a source port or check for inclusion in port-range

    The value is the tuple (port, last_port) where last_port may be ``None``
    """
    def __init__(self, match: Match):
        super().__init__(match, '--sport', sep=':')


class DestPortCriterion(NumberOrRangeCriterion):
    """Compare against a destination port or check for inclusion in port-range

    The value is the tuple (port, last_port) where last_port may be ``None``
    """
    def __init__(self, match: Match):
        super().__init__(match, '--dport', sep=':')


class TcpOptionCriterion(GenericCriterion):
    """Compare against a TCP option number.

    The value is an integer.
    """
    def __init__(self, match: Match):
        super().__init__(match, '--tcp-option')


class _PortParser:      # pylint: disable=too-few-public-methods
    """Helper class used to parse TCP/UDP port criteria
    """

    SOURCE_PORT_PREFIX = ('spt:', 'spts:')
    DEST_PORT_PREFIX = ('dpt:', 'dpts:')
    PORT_PREFIX = SOURCE_PORT_PREFIX + DEST_PORT_PREFIX

    @classmethod
    def parse(cls, port_match_str: str, match: Match):
        """Add the proper criterion to 'match'
        """
        if port_match_str.startswith(cls.SOURCE_PORT_PREFIX):
            port_crit = match.source_port()
        else:
            port_crit = match.dest_port()
        port_spec = port_match_str.split(':', 1)[1]
        is_equal, port_spec = MatchParser.parse_value(port_spec)
        if ':' not in port_spec:
            port_crit.compare(is_equal, int(port_spec))
            return
        ports = port_spec.split(':', 1)
        port_crit.compare(is_equal, int(ports[0]), int(ports[1]))


class TcpMatch(Match):
    """Match against the fields of the TCP header
    """

    def __init__(self):
        self.__flags_crit = None
        self.__src_port_crit = None
        self.__dest_port_crit = None
        self.__tcp_option_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name,
        in this case, ``tcp``
        """
        return 'tcp'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the TCP match criteria: flags, source-port, dest-port,
        tcp-option
        """
        return (self.__flags_crit, self.__src_port_crit,
                        self.__dest_port_crit, self.__tcp_option_crit)

    def syn(self) -> TcpFlagsCriterion:
        """Criterion for matching against a SYN packet
        """
        if self.__flags_crit is None:
            self.__flags_crit = TcpFlagsCriterion(self, syn_only=True)
        return self.__flags_crit

    def tcp_flags(self) -> TcpFlagsCriterion:
        """Compare with TCP flags
        """
        if self.__flags_crit is None:
            self.__flags_crit = TcpFlagsCriterion(self)
        return self.__flags_crit

    def source_port(self) -> SourcePortCriterion:
        """Matching against the source port
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

    def tcp_option(self) -> TcpOptionCriterion:
        """Match against a TCP option
        """
        if self.__tcp_option_crit is None:
            self.__tcp_option_crit = TcpOptionCriterion(self)
        return self.__tcp_option_crit

    @staticmethod
    def __parse_tcp_flags_num(numstr: int) -> Set[TcpFlag]:
        """Parse a hex-value numstr (e.g. 0x11) into a set of TCP flags.
        """
        try:
            flag_mask = int(numstr, 16)
            flags = {flag for flag in TcpFlag if flag_mask & flag}
            return flags
        except ValueError as valerr:
            raise IptablesParsingError(
                        "Bad TCP flag mask: " + numstr) from valerr

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse the TCP criteria. The iptables output looks like this::

                tcp dpt:20 option=!10 flags:0x17/0x02

        The 'tcp' field has already been consumed.

        :meta private:
        """
        criteria_iter = parser.get_iter()
        match = TcpMatch()
        for val in criteria_iter:
            if val.startswith('flags:'):
                flag_spec = val.split(':', 1)[1]
                is_equal, flag_spec = parser.parse_value(flag_spec)
                if '/' not in flag_spec:
                    raise IptablesParsingError(
                                f"no '/' in TCP flags: {flag_spec}")
                mask, comp = flag_spec.split('/', 1)
                flags_checked = cls.__parse_tcp_flags_num(mask)
                flags_set = cls.__parse_tcp_flags_num(comp)
                if (flags_set == {TcpFlag.SYN} and
                        flags_checked == {TcpFlag.FIN, TcpFlag.SYN,
                                                TcpFlag.RST, TcpFlag.ACK}):
                    match.syn().compare(is_equal)
                else:
                    match.tcp_flags().compare(is_equal,
                                                flags_checked, flags_set)
            elif val.startswith(_PortParser.PORT_PREFIX):
                _PortParser.parse(val, match)
            elif val.startswith('option'):
                # The comparison looks either like 'option=10' or 'option=!10'
                is_equal, value = parser.parse_value(val[len('option')+1:])
                match.tcp_option().compare(is_equal, int(value))
            else:
                criteria_iter.put_back(val)
                break
        return match


MatchParser.register_match('tcp', TcpMatch)
