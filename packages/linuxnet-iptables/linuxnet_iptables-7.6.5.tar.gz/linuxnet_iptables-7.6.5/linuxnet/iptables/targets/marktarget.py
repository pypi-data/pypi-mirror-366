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
This module provides the MarkTarget class which provides access to
the iptables MARK target.
"""

from typing import List, Optional

from ..deps import get_logger
from ..exceptions import IptablesParsingError, IptablesError

from .target import Target, TargetParser

_logger = get_logger("linuxnet.iptables.target.marktarget")


class _MarkOperations:
    """Mixin class to provide mark-related operations
    """

    #
    # Mark operations
    #
    SET = 1
    XSET = 2
    AND = 3
    OR = 4
    XOR = 5

    NOMASK = 0xffffffff

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__value = None
        self.__mask = None
        self.__op = None

    def get_mark(self) -> Optional[int]:
        """Returns the mark value set by this target
        """
        return self.__value

    def get_mask(self) -> Optional[int]:
        """Returns the mask used by this target
        """
        return self.__mask

    def get_op(self) -> Optional[int]:
        """Returns the operation

        :rtype: an integer with one of the following values:
                `SET`, `XSET`, `AND`, `OR`, `XOR`,
                or ``None``
        """
        return self.__op

    def set_mark(self, value: int, mask: Optional[int] =None) -> Target:
        """Perform the operation::

                mark = (mark AND NOT(mask)) OR value

        If ``mask`` is not present, the operation becomes ``mark = value``.
        """
        self._assert_no_action()
        self.__value = value
        self.__mask = mask if mask is not None else self.NOMASK
        self.__op = self.SET
        return self

    def set_xmark(self, value: int, mask: Optional[int] =None) -> Target:
        """Perform the operation::

                mark = (mark AND NOT(mask)) XOR value

        If ``mask`` is not present, the operation becomes ``mark = value``.
        """
        self._assert_no_action()
        self.__value = value
        self.__mask = mask if mask is not None else self.NOMASK
        self.__op = self.XSET
        return self

    def and_mark(self, mask: int) -> Target:
        """Clear the bits identified by mask
        """
        self._assert_no_action()
        self.__value = None
        self.__mask = mask
        self.__op = self.AND
        return self

    def or_mark(self, mask: int) -> Target:
        """Set the bits identified by mask
        """
        self._assert_no_action()
        self.__value = None
        self.__mask = mask
        self.__op = self.OR
        return self

    def xor_mark(self, mask: int) -> Target:
        """Xor the bits identified by mask
        """
        self._assert_no_action()
        self.__value = None
        self.__mask = mask
        self.__op = self.XOR
        return self

    def _assert_no_action(self) -> None:
        """Raise an IptablesError if an op has already been specified.
        """
        if self.__op is not None:
            raise IptablesError(f'mark operation already set: {self.__op}')

    def parse_op(self, val: str, field_iter) -> bool:
        """Parse the operation identified by 'val'

        :meta private:
        """
        if val == 'set':
            self.set_mark(int(field_iter.next_value(val), 16))
        elif val == 'xset':
            field = field_iter.next_value(val)
            valstr, maskstr = field.split('/', 1)
            self.set_xmark(int(valstr, 16), int(maskstr, 16))
        elif val == 'or':
            self.or_mark(int(field_iter.next_value(val), 16))
        elif val == 'xor':
            self.xor_mark(int(field_iter.next_value(val), 16))
        elif val == 'and':
            self.and_mark(int(field_iter.next_value(val), 16))
        else:
            return False
        return True

    def mark_iptables_args(self, args: List[str]) -> List[str]:
        """Converts the op/value/mask to a list of **iptables(8)** arguments
        for the MARK target

        :meta private:
        """
        if self.__value is None and self.__mask is None:
            raise IptablesError("no mark operation specified")
        if self.__op in (self.SET, self.XSET):
            if self.__op == self.SET:
                args.append('--set-mark')
            else:
                args.append('--set-xmark')
            if self.__mask == self.NOMASK:
                args.append(f'0x{self.__value:x}')
            else:
                args.append(f'0x{self.__value:x}/0x{self.__mask:x}')
        elif self.__op == self.AND:
            args.extend(['--and-mark', f'0x{self.__mask:x}'])
        elif self.__op == self.OR:
            args.extend(['--or-mark', f'0x{self.__mask:x}'])
        elif self.__op == self.XOR:
            args.extend(['--xor-mark', f'0x{self.__mask:x}'])
        else:
            raise IptablesError(f"unexpected mark operation: {self.__op}")
        return args


class MarkTarget(_MarkOperations, Target):
    """This class provides access to the ``MARK`` target
    """
    def __init__(self, mark: Optional[int] =None):
        """
        :param mark: value used to set the mark value in the packet
        """
        super().__init__('MARK', terminates=False)
        if mark is not None:
            self.set_mark(mark)

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        retval = super().to_iptables_args()
        return self.mark_iptables_args(retval)

    @classmethod
    def parse(cls, parser: TargetParser) -> Target:
        """Parse the MARK target options

        :meta private:
        """
        field_iter = parser.get_field_iter()
        target = MarkTarget()
        for val in field_iter:
            if not target.parse_op(val, field_iter):
                raise IptablesParsingError(f'unknown MARK argument: {val}')
        return target


TargetParser.register_target('MARK', MarkTarget, 'MARK')
