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
This module provides the PacketMatch class which supports
matching against standard packet attributes
"""

from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address
from typing import Iterable, List, Optional, Union

from ..exceptions import IptablesError, IptablesParsingError
from ..deps import get_logger

from .match import Criterion, Match, MatchParser
from .util import BooleanCriterion, GenericCriterion

_logger = get_logger('linuxnet.iptables.matches.packetmatch')


class InputInterfaceCriterion(GenericCriterion):
    """Compare with the input interface.

    The comparison value is an interface name (a string).
    """
    def __init__(self, match: Match):
        super().__init__(match, '-i')


class OutputInterfaceCriterion(GenericCriterion):
    """Compare with the output interface.

    The comparison value is an interface name (a string).
    """
    def __init__(self, match: Match):
        super().__init__(match, '-o')


class AddressCriterion(Criterion):
    """Compare against an IPv4/IPv6 address.

    The comparison value is an :class:`IPv4Network` or an :class:`IPv6Network`
    """
    def __init__(self, match: Match, iptables_option: str,
                                ipv6: Optional[bool]):
        """
        :param match: the owner :class:`Match`
        :param iptables_option: the **iptables(8)** option to use when
            generating the iptables arguments
        :param ipv6: if ``True``, assume IPv6 addresses, otherwise assume
            IPv4 addresses
        """
        super().__init__(match)
        self.__option = iptables_option
        self.__ipv6 = ipv6
        self.__value = None

    def get_iptables_option(self) -> str:
        """Returns the **iptables(8)** option
        """
        return self.__option

    def get_value(self) -> Union[IPv4Network, IPv6Network, None]:
        """Returns the criterion value
        """
        return self.__value

    def equals(self,                    # pylint: disable=arguments-differ
        value: Union[IPv4Network, IPv6Network,
                        IPv4Address, IPv6Address, str]) -> Match:
        """Compare with the specified value, which can be specified as
        an :class:`IPv4Network`, an :class:`IPv6Network`,
        an :class:`IPv4Address`, an :class:`IPv6Address`, or as
        a string. Internally the value is always stored as
        an :class:`IPv4Network`, or an :class:`IPv6Network`.
        """
        if isinstance(value, str):
            try:
                if ':' in value:
                    value = IPv6Network(value)
                else:
                    value = IPv4Network(value)
            except Exception as ex:
                raise IptablesError(
                    f"{value} cannot be parsed as IPv4/IPv6 address") from ex
        elif isinstance(value, IPv4Address):
            value = IPv4Network(value)
        elif isinstance(value, IPv6Address):
            value = IPv6Network(value)
        if isinstance(value, IPv4Network):
            if self.__ipv6 is not None:
                if self.__ipv6:
                    raise IptablesError(
                        f"criterion expects IPv6 address (got {value}")
            else:
                self.__ipv6 = False
        elif isinstance(value, IPv6Network):
            if self.__ipv6 is not None:
                if not self.__ipv6:
                    raise IptablesError(
                        f"criterion expects IPv4 address (got {value}")
            else:
                self.__ipv6 = True
        else:
            raise IptablesError(
                        f"criterion expects IPv4/IPv6 address (got {value}")
        self.__value = value
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Convert to **iptables(8)** arguments
        """
        return [self.__option, str(self.__value)]


class SourceAddressCriterion(AddressCriterion):
    """Compare with the source address.

    The comparison value is an :class:`IPv4Network` or an :class:`IPv6Network`
    """
    def __init__(self, match: Match, *, ipv6: Optional[bool] =None):
        """
        :param match: the owner :class:`PacketMatch`
        :param ipv6: if ``True``, assume IPv6 addresses, otherwise assume
            IPv4 addresses
        """
        super().__init__(match, '-s', ipv6)


class DestAddressCriterion(AddressCriterion):
    """Compare with the destination address.

    The comparison value is an :class:`IPv4Network` or an :class:`IPv6Network`
    """
    def __init__(self, match: Match, *, ipv6: bool):
        """
        :param match: the owner :class:`PacketMatch`
        :param ipv6: if ``True``, assume IPv6 addresses, otherwise assume
            IPv4 addresses
        """
        super().__init__(match, '-d', ipv6)


class ProtocolCriterion(Criterion):
    """Compare with the protocol.

    The comparison value is a protocol name (a string); it may also
    be a number in string form if there is no mapping of that number
    to a protocol name in ``/etc/protocols``.
    """

    # Key: protocol number
    # Value: protocol name
    __proto_map = {}
    __proto_map_ready = False

    def __init__(self, match: Match):
        super().__init__(match)
        self.__proto_name = None

    @classmethod
    def __getprotobynumber(cls, protonum: int) -> Optional[str]:
        """Returns the protocol name for the specified protocol
        """
        if cls.__proto_map_ready:
            return cls.__proto_map.get(protonum)
        try:
            with open("/etc/protocols", encoding="utf-8") as protofile:
                for line in protofile:
                    pos = line.find('#')
                    if pos < 0:
                        line = line.strip()
                    else:
                        line = line[:pos].strip()
                    if not line:
                        continue
                    fields = line.split()
                    if len(fields) < 2:
                        continue
                    try:
                        cls.__proto_map[int(fields[1])] = fields[0]
                    except ValueError:
                        pass
        except Exception:               # pylint: disable=broad-except
            _logger.exception("unable to process /etc/protocols")
        finally:
            cls.__proto_map_ready = True
        return cls.__proto_map.get(protonum)

    def get_value(self) -> str:
        """Return protocol name
        """
        return self.__proto_name

    def equals(self, proto) -> Match:   # pylint: disable=arguments-differ
        """Compare with the specified protocol.

        :param proto: the parameter can a string or an integer; if it
            is an integer, it will be converted to the corresponding
            protocol name, if possible, otherwise it will be used as-is
            in string form (i.e. 199 will be converted to "199")
        """
        if isinstance(proto, str):
            # Check if is a number in string form
            try:
                self.__proto_name = self.__getprotobynumber(int(proto)) or proto
            except ValueError:
                self.__proto_name = proto
        elif isinstance(proto, int):
            self.__proto_name = self.__getprotobynumber(int(proto)) or \
                                                str(proto)
        else:
            raise IptablesError(f'unexpected argument type: {proto}')
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified protocol
        """
        return ['-p', self.__proto_name]


class FragmentCriterion(BooleanCriterion):
    """Check if a packet is a fragment.
    """

    def __init__(self, match: Match):
        super().__init__(match, '-f')


class PacketMatch(Match):
    """This class provides matching against the following attributes of
    a packet:

    * input interface
    * output interface
    * protocol
    * source address
    * destination address
    * fragment bit (IPv4-only)

    """

    def __init__(self, *, ipv6=False):
        """
        :param ipv6: optional boolean to indicate IPv6 address matching when
            ``True``; the default is IPv4
        """
        self._ipv6 = ipv6
        self.__iif_crit = None
        self.__oif_crit = None
        self.__proto_crit = None
        self.__frag_crit = None
        self.__source_crit = None
        self.__dest_crit = None

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        if self._ipv6 != other._ipv6:
            raise IptablesError(
                f'Protocol mismatch: {self._ipv6=}, {other._ipv6=}')
        return super().__eq__(other)

    @staticmethod
    def get_match_name() -> Optional[str]:
        """Returns the **iptables(8)** match extension name. In the case of
        the standard packet match, there is no name.
        """
        return None

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the packet match criteria: input-interface, output-interface,
        protocol, fragmented, source, destination.
        """
        return (
                            self.__iif_crit,
                            self.__oif_crit,
                            self.__proto_crit,
                            self.__frag_crit,
                            self.__source_crit,
                            self.__dest_crit,
                        )

    def protocol(self) -> ProtocolCriterion:
        """Match against the protocol
        """
        if self.__proto_crit is None:
            self.__proto_crit = ProtocolCriterion(self)
        return self.__proto_crit

    def input_interface(self) -> InputInterfaceCriterion:
        """Match against the input interface
        """
        if self.__iif_crit is None:
            self.__iif_crit = InputInterfaceCriterion(self)
        return self.__iif_crit

    def output_interface(self) -> OutputInterfaceCriterion:
        """Match against the output interface
        """
        if self.__oif_crit is None:
            self.__oif_crit = OutputInterfaceCriterion(self)
        return self.__oif_crit

    def source_address(self) -> SourceAddressCriterion:
        """Match against the source address
        """
        if self.__source_crit is None:
            self.__source_crit = SourceAddressCriterion(self, ipv6=self._ipv6)
        return self.__source_crit

    def dest_address(self) -> DestAddressCriterion:
        """Match against the destination address
        """
        if self.__dest_crit is None:
            self.__dest_crit = DestAddressCriterion(self, ipv6=self._ipv6)
        return self.__dest_crit

    def fragment(self) -> FragmentCriterion:
        """Match if packet has (or has not) the fragment bit set
        """
        if self._ipv6:
            raise IptablesError(
                        'PacketMatch has no fragment criterion for IPv6')
        if self.__frag_crit is None:
            self.__frag_crit = FragmentCriterion(self)
        return self.__frag_crit

    @classmethod
    def _parse(cls, field_iter, *, ipv6: bool) -> Optional['PacketMatch']:
        """Parse the following fields, which will be returned in-order
        from field_iter:
            protocol, options, input-interface, output-interface,
            source, destination
        Returns a :class:`PacketMatch` object if any criteria for the above
        fields are defined, otherwise ``None``

        :param field_iter: an iterator that returns the fields of an
            **iptables(8)** output line starting with the protocol field

        :meta private:
        """
        packet_match = PacketMatch(ipv6=ipv6)
        proto = next(field_iter)
        # The absence of a specific protocol is indicated via 'all'
        # (iptables-1.8.5), or '0' (iptables-nft-1.8.10)
        if proto not in ('all', '0'):
            is_equal, proto = MatchParser.parse_value(proto)
            packet_match.protocol().compare(is_equal, proto)
        # We currently expect the 'option' field to be absent for IPv6
        if not ipv6:
            opt = next(field_iter)
            if opt == '--':
                pass
            elif opt == '-f':
                packet_match.fragment().equals()
            elif opt == '!f':
                packet_match.fragment().not_equals()
            else:
                raise IptablesParsingError(f'cannot parse option: {opt}')
        iif = next(field_iter)
        if iif != '*':
            is_equal, interface_name = MatchParser.parse_value(iif)
            packet_match.input_interface().compare(is_equal, interface_name)
        oif = next(field_iter)
        if oif != '*':
            is_equal, interface_name = MatchParser.parse_value(oif)
            packet_match.output_interface().compare(is_equal, interface_name)
        source = next(field_iter)
        if ipv6:
            anyipstr = '::/0'
            klass = IPv6Network
        else:
            anyipstr = '0.0.0.0/0'
            klass = IPv4Network
        if source != anyipstr:
            is_equal, addr = MatchParser.parse_value(source)
            packet_match.source_address().compare(is_equal, klass(addr))
        dest = next(field_iter)
        if dest != anyipstr:
            is_equal, addr = MatchParser.parse_value(dest)
            packet_match.dest_address().compare(is_equal, klass(addr))
        return packet_match if packet_match.has_criteria() else None
