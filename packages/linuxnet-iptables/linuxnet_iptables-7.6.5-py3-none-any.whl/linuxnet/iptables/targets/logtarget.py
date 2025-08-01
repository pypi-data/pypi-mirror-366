# Copyright (c) 2021, 2022, 2023, 2024, 2025, Panagiotis Tsirigotis

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
This module provides the LogTarget class which provides access to
the iptables LOG target.
"""

from typing import List, Optional

from ..deps import get_logger
from ..exceptions import IptablesParsingError

from .target import Target, TargetParser

_logger = get_logger("linuxnet.iptables.targets.logtarget")


class LogTarget(Target):
    """This class provides access to the ``LOG`` target
    """

    __OPT_MAP = {
                   '--log-tcp-sequence' : 0x1,
                   '--log-tcp-options'  : 0x2,
                   '--log-ip-options'   : 0x4,
                   '--log-uid'          : 0x8,
                   '--log-macdecode'    : 0x20,
                }
    __ALL_FLAGS = sum(__OPT_MAP.values())

    def __init__(self,          # pylint: disable=too-many-arguments
                        log_prefix: Optional[str] =None,
                        log_level: Optional[str] =None,
                        *,
                        log_tcp_sequence=False,
                        log_tcp_options=False,
                        log_ip_options=False,
                        log_uid=False,
                        log_macdecode=False):
        """
        :param log_prefix: prefix to include in every log message
        :param log_level: log level; see **syslog(3)** for possible
            values, e.g. ``info`` (note that the **LOG_** prefix is
            stripped); numbers in string form (e.g. "5") are also accepted
        :param log_tcp_sequence: optional boolean (see **iptables(8)** **LOG**
           target)
        :param log_tcp_options: optional boolean (see **iptables(8)** **LOG**
           target)
        :param log_ip_options: optional boolean (see **iptables(8)** **LOG**
           target)
        :param log_uid: optional boolean (see **iptables(8)** **LOG** target)
        :param log_macdecode: optional boolean (see **iptables(8)** **LOG**
            target)
        """
        super().__init__('LOG', terminates=False)
        self.__log_prefix = log_prefix
        self.__log_level = log_level
        self.__log_flags = 0
        if log_tcp_sequence:
            self.log_tcp_sequence()
        if log_tcp_options:
            self.log_tcp_options()
        if log_ip_options:
            self.log_ip_options()
        if log_uid:
            self.log_uid()
        if log_macdecode:
            self.log_macdecode()

    def _set_log_flags(self, flags: int) -> None:
        """Helper method used by the parsing code
        """
        self.__log_flags = flags

    def get_log_prefix(self) -> Optional[str]:
        """Returns the log prefix
        """
        return self.__log_prefix

    def get_log_level(self) -> Optional[str]:
        """Returns the log level
        """
        return self.__log_level

    def is_logging_tcp_sequence(self) -> bool:
        """Returns ``True`` if the ``--log-tcp-sequence`` option is set.
        """
        return (self.__log_flags & self.__OPT_MAP['--log-tcp-sequence']) != 0

    def log_tcp_sequence(self) -> Target:
        """Set the ``--log-tcp-sequence`` option.
        """
        self.__log_flags |= self.__OPT_MAP['--log-tcp-sequence']
        return self

    def is_logging_tcp_options(self) -> bool:
        """Returns ``True`` if the ``--log-tcp-options`` option is set.
        """
        return (self.__log_flags & self.__OPT_MAP['--log-tcp-options']) != 0

    def log_tcp_options(self) -> Target:
        """Set the ``--log-tcp-options`` option.
        """
        self.__log_flags |= self.__OPT_MAP['--log-tcp-options']
        return self

    def is_logging_ip_options(self) -> bool:
        """Returns ``True`` if the ``--log-ip-options`` option is set.
        """
        return (self.__log_flags & self.__OPT_MAP['--log-ip-options']) != 0

    def log_ip_options(self) -> Target:
        """Set the ``--log-ip-options`` option.
        """
        self.__log_flags |= self.__OPT_MAP['--log-ip-options']
        return self

    def is_logging_uid(self) -> bool:
        """Returns ``True`` if the ``--log-uid`` option is set.
        """
        return (self.__log_flags & self.__OPT_MAP['--log-uid']) != 0

    def log_uid(self) -> Target:
        """Set the ``--log-uid`` option.
        """
        self.__log_flags |= self.__OPT_MAP['--log-uid']
        return self

    def log_macdecode(self) -> Target:
        """Set the ``--log-macdecode`` option.
        """
        self.__log_flags |= self.__OPT_MAP['--log-macdecode']
        return self

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        retval = super().to_iptables_args()
        if self.__log_prefix:
            retval += ['--log-prefix', self.__log_prefix]
        if self.__log_level:
            retval += ['--log-level', self.__log_level]
        for option, flag in self.__OPT_MAP.items():
            if self.__log_flags & flag:
                retval.append(option)
        return retval

    @classmethod
    def parse(cls, parser: TargetParser) -> Target:
        """Parse the LOG target options

        :meta private:
        """
        log_level = None
        log_prefix = None
        log_flags = 0
        field_iter = parser.get_field_iter()
        for val in field_iter:
            if val == 'flags':
                flags = int(field_iter.next_value(val))
                unknown_flags = flags & ~cls.__ALL_FLAGS
                if unknown_flags:
                    raise IptablesParsingError(
                            f'unknown LOG target flags: {unknown_flags:#x}')
                log_flags = flags
            elif val == 'level':
                log_level = field_iter.next_value(val)
            elif val == 'prefix':
                # Consume the rest of the fields
                val = ' '.join(field_iter)
                # Backquote used by iptables 1.4.7, double quote used
                # by iptables 1.8.4
                if val[0] in ("`", '"'):
                    val = val[1:-1]
                log_prefix = val
            else:
                raise IptablesParsingError(f'unknown target option: {val}')
        target = LogTarget(log_prefix, log_level)
        target._set_log_flags(log_flags)
        return target


TargetParser.register_target('LOG', LogTarget, 'LOG')
