# Copyright (c) 2022, 2023, Panagiotis Tsirigotis

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
linuxnet.iptables library
~~~~~~~~~~~~~~~~~~~~~~~~~

The linuxnet.iptables library provides programmatic access for
packet filtering using the Linux **iptables(8)** command.
"""

from .matches import *
from .targets import *

from .rule import ChainRule
from .chain import Chain, BuiltinChain
from .table import IptablesPacketFilterTable

from .exceptions import (
        IptablesError,
        IptablesParsingError,
        IptablesExecutionError,
        )
