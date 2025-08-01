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
Available match classes
"""

from .match import Match, MatchNone, Criterion
from .addrtypematch import AddressTypeMatch
from .commentmatch import CommentMatch
from .connbytesmatch import ConnbytesMatch
from .connmarkmatch import ConnmarkMatch
from .conntrackmatch import ConntrackMatch
from .icmpmatch import IcmpMatch
from .lengthmatch import LengthMatch
from .limitmatch import LimitMatch
from .macmatch import MacMatch
from .markmatch import MarkMatch
from .multiportmatch import MultiportMatch
from .ownermatch import OwnerMatch
from .packetmatch import PacketMatch
from .packettypematch import PacketTypeMatch
from .recentmatch import RecentMatch
from .setmatch import SetMatch
from .statematch import StateMatch
from .statisticmatch import StatisticMatch
from .tcpmatch import TcpMatch, TcpFlag
from .ttlmatch import TtlMatch
from .tcpmssmatch import TcpmssMatch
from .udpmatch import UdpMatch
