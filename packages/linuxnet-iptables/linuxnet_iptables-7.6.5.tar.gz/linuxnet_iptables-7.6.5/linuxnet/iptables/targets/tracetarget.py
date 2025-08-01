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
This module provides the TraceTarget class which provides access to
the iptables TRACE target.
"""

from ..deps import get_logger

from .target import Target, TargetParser

_logger = get_logger("linuxnet.iptables.target.notracktarget")


class TraceTarget(Target):
    """This class provides access to the ``TRACE`` target
    """
    def __init__(self):
        """The :meth:`__init__` method expects no arguments.
        """
        super().__init__('TRACE', terminates=False)

    @classmethod
    def parse(cls, _) -> Target:
        """Parse the TRACE target

        :meta private:
        """
        return TraceTarget()


TargetParser.register_target('TRACE', TraceTarget)
