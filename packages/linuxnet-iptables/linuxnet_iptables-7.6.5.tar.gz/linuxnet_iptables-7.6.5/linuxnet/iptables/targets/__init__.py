# Copyright (c) 2023, 2025, Panagiotis Tsirigotis

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
Available target classes
"""

from .target import Target, Targets, TargetNone, ChainTarget, UnparsedTarget
from .connmarktarget import ConnmarkTarget
from .logtarget import LogTarget
from .nattarget import SnatTarget, DnatTarget
from .nflogtarget import NFLogTarget
from .marktarget import MarkTarget
from .masqueradetarget import MasqueradeTarget
from .notracktarget import NoTrackTarget
from .rejecttarget import RejectTarget
from .settarget import SetTarget
from .tracetarget import TraceTarget
from .ttltarget import TtlTarget
