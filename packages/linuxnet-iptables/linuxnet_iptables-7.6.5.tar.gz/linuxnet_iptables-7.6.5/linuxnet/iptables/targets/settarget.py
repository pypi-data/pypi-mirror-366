# Copyright (c) 2025, Panagiotis Tsirigotis

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
This module provides the SetTarget class which provides access to
the iptables SET target.
"""

from typing import List, Optional

from ..deps import get_logger
from ..exceptions import IptablesError, IptablesParsingError

from .target import Target, TargetParser

_logger = get_logger("linuxnet.iptables.targets.settarget")


class SetTarget(Target):
    """This class provides access to the ``SET`` target
    """

    #: Add operation
    ADD_SET = 1
    #: Delete operation
    DEL_SET = 2

    _op_map = {
                ADD_SET : "--add-set",
                DEL_SET : "--del-set",
            }

    def __init__(self,
                        operation: int,
                        ipset_name: str,
                        ipset_flags: List[str],
                        *,
                        timeout: Optional[int] =None,
                        exist: Optional[bool] = False):
        """
        :param operation: identifies what ipset operation to perform;
            possible values include ``SetTarget.ADD_SET`` or
            ``SetTarget.DEL_SET``
        :param ipset_name: name of ipset
        :param ipset_flags: list of flags identifying packet data; at
            least one flag must be present, otherwise an
            :exc:`IptablesError` exception will be raised
        :param timeout: timeout value for added entries
        :param exist: if ``True``, reset timeout when adding an entry
            that exists already
        """
        if operation not in (self.ADD_SET, self.DEL_SET):
            raise IptablesError(
                f"unknown operation for SET target: {operation}")
        super().__init__('SET', terminates=False)
        self.__operation = operation
        self.__ipset_name = ipset_name
        self.__ipset_flags = ipset_flags
        self.__timeout = timeout
        self.__exist = exist

    def get_ipset_name(self) -> str:
        """Returns the ipset name
        """
        return self.__ipset_name

    def get_ipset_flags(self) -> List[str]:
        """Returns the ipset flags
        """
        return self.__ipset_flags

    def get_operation(self) -> int:
        """Returns the operation
        """
        return self.__operation

    def is_updating_existing(self) -> bool:
        """Returns ``True`` if the ``--exist`` option is set.
        """
        return self.__exist

    def update_existing(self) -> Target:
        """Set the ``--exist`` option.
        """
        self.__exist = True
        return self

    def get_timeout(self) -> Optional[int]:
        """Returns the timeout, or ``None``
        """
        return self.__timeout

    def set_timeout(self, timeout: Optional[int]) -> Target:
        """Set the timeout value for entries added to the ipset.
        """
        self.__timeout = timeout
        return self

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        retval = super().to_iptables_args()
        retval.append(self._op_map[self.__operation])
        retval.append(self.__ipset_name)
        retval.append(",".join(self.__ipset_flags))
        if self.__timeout:
            retval.extend(["--timeout", str(self.__timeout)])
        if self.__exist:
            retval.append("--exist")
        return retval

    @classmethod
    def parse(cls, parser: TargetParser) -> Target:
        """Parse the SET target options

        The target part of the rule looks like this:
               add-set testchain_set src,dst exist timeout 100

        :meta private:
        """
        timeout = None
        exist = False
        operation = 0
        field_iter = parser.get_field_iter()
        field_iter.rewind()
        opstr = next(field_iter)
        if opstr == 'add-set':
            operation = cls.ADD_SET
        elif opstr == 'del-set':
            operation = cls.DEL_SET
        else:
            raise IptablesParsingError(f'unknown SET target operation: {opstr}')
        ipset_name = next(field_iter)
        flagstr = next(field_iter)
        for val in field_iter:
            if val == 'exist':
                exist = True
            elif val == 'timeout':
                timeout = int(field_iter.next_value(val))
            else:
                raise IptablesParsingError(f'unknown target option: {val}')
        target = SetTarget(operation, ipset_name, flagstr.split(','),
                                timeout=timeout, exist=exist)
        return target


TargetParser.register_target('SET', SetTarget, ('add-set', 'del-set'))
