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
This module provides the RejectTarget class which provides access to
the iptables REJECT target.
"""

from typing import List, Optional

from ..deps import get_logger

from .target import Target, TargetParser

_logger = get_logger("linuxnet.iptables.targets.rejecttarget")


class RejectTarget(Target):
    """This class provides access to the ``REJECT`` target
    """
    def __init__(self, reject_with: Optional[str] =None):
        """
        :param reject_with: optional ``ICMP`` message type
            (see **iptables(8)** **REJECT** target)
        """
        super().__init__('REJECT', terminates=True)
        self.__reject_with = reject_with

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        retval = super().to_iptables_args()
        if self.__reject_with is not None:
            retval += ['--reject-with', self.__reject_with]
        return retval

    def get_rejection_message(self) -> Optional[str]:
        """Returns the ICMP rejection message.
        """
        return self.__reject_with

    @classmethod
    def parse(cls, parser: TargetParser) -> Target:
        """Parse the REJECT target options

        :meta private:
        """
        field_iter = parser.get_field_iter()
        icmp_message = field_iter.next_value('reject-with')
        return RejectTarget(reject_with=icmp_message)

TargetParser.register_target('REJECT', RejectTarget, 'reject-with')
