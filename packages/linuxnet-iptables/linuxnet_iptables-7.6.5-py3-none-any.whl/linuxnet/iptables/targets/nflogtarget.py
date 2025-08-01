# Copyright (c) 2024, Panagiotis Tsirigotis

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
This module provides the NFLogTarget class which provides access to
the iptables NFLOG target.
"""

from typing import List, Optional

from ..deps import get_logger
from ..exceptions import IptablesParsingError

from .target import Target, TargetParser

_logger = get_logger("linuxnet.iptables.targets.logtarget")


class NFLogTarget(Target):
    """This class provides access to the ``NFLOG`` target
    """

    def __init__(self, *,       # pylint: disable=too-many-arguments
                        group: Optional[int] = None,
                        prefix: Optional[str] =None,
                        size: Optional[int] =None,
                        threshold: Optional[int] =None):
        """
        :param group: netlink group to send packets to
        :param prefix: prefix to include in every log message
        :param size: number of packets to copy to userspace
        :param threshold: number of packets to queue in kernel before
            sending to userspace
        """
        super().__init__('NFLOG', terminates=False)
        self.__group = group
        self.__prefix = prefix
        self.__size = size
        self.__threshold = threshold

    def get_nflog_group(self) -> Optional[int]:
        """Returns the nflog group
        """
        return self.__group

    def get_nflog_prefix(self) -> Optional[str]:
        """Returns the nflog prefix
        """
        return self.__prefix

    def get_nflog_size(self) -> Optional[int]:
        """Returns the nflog size
        """
        return self.__size

    def get_nflog_threshold(self) -> Optional[int]:
        """Returns the nflog threshold
        """
        return self.__threshold

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        retval = super().to_iptables_args()
        if self.__group:
            retval += ['--nflog-group', str(self.__group)]
        if self.__prefix:
            retval += ['--nflog-prefix', self.__prefix]
        if self.__size:
            retval += ['--nflog-size', str(self.__size)]
        if self.__threshold:
            retval += ['--nflog-threshold', str(self.__threshold)]
        return retval

    @classmethod
    def parse(cls, parser: TargetParser) -> Target:
        """Parse the NFLOG target options

        :meta private:
        """
        nflog_group = None
        nflog_prefix = None
        nflog_size = None
        nflog_threshold = None
        field_iter = parser.get_field_iter()
        field_iter.rewind()
        for val in field_iter:
            if val == 'nflog-group':
                nflog_group = int(field_iter.next_value(val))
            elif val == 'nflog-threshold':
                nflog_threshold = int(field_iter.next_value(val))
            elif val == 'nflog-size':
                nflog_size = int(field_iter.next_value(val))
            elif val == 'nflog-range':
                _logger.warning("ignoring nflog-range option")
                _ = field_iter.next_value(val)
            elif val == 'nflog-prefix':
                prefix = field_iter.next_value(val)
                if prefix[0] == '"':
                    #
                    # Consume fields until the one containing the
                    # closing double-quote is located.
                    #
                    while True:
                        field = next(field_iter)
                        prefix += ' ' + field
                        # We are done if the last field character is
                        # a back-quote, which is not back-slash escaped
                        if (field[-1] == '"' and
                                (len(field) == 1 or field[-2] != "\\")):
                            break
                    # truncate double-quotes
                    nflog_prefix = prefix[1:-1]
                else:
                    nflog_prefix = prefix
            else:
                raise IptablesParsingError(f'unknown target option: {val}')
        target = NFLogTarget(group=nflog_group, prefix=nflog_prefix,
                                size=nflog_size, threshold=nflog_threshold)
        return target


TargetParser.register_target('NFLOG', NFLogTarget, 'nflog-', prefix_match=True)
