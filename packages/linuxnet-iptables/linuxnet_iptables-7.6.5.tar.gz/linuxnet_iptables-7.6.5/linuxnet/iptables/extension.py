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
This module provides access to functions and classes that can be used
to extend the functionality of this package by adding support
for new matches and/or targets.
"""

# pylint: disable=unused-import

from .exceptions import IptablesError, IptablesParsingError
from .matches.match import (
                        Match,
                        MatchParser,
                        Criterion,
                        CriteriaExhaustedError,
                        )
from .matches.util import (
                        BooleanCriterion,
                        GenericCriterion,
                        GenericPositiveCriterion,
                        )
from .parsing import LookaheadIterator, RuleFieldIterator
from .targets.target import Target, TargetParser
