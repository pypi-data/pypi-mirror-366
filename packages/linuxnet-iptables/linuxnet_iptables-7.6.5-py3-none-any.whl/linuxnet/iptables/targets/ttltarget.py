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
This module provides the TtlTarget class which provides access to
the iptables TTL target.
"""

from typing import List, Optional

from ..deps import get_logger
from ..exceptions import IptablesParsingError, IptablesError

from .target import Target, TargetParser

_logger = get_logger("linuxnet.iptables.target.ttltarget")


class TtlTarget(Target):
    """This class provides access to the ``TTL`` target
    """
    def __init__(self,
                        set_ttl_to: Optional[int] =None,
                        inc_ttl_by: Optional[int] =None,
                        dec_ttl_by: Optional[int] =None):
        """
        :param set_ttl_to: set the TTL to this value
        :param inc_ttl_by: increase the TTL by this value
        :param dec_ttl_by: decrease the TTL by this value

        Exactly one of ``set_ttl_to``, ``inc_ttl_by``,
        ``dec_ttl_by`` should not be equal to ``None``.
        """
        super().__init__('TTL', terminates=False)
        self.__set_ttl_to = set_ttl_to
        self.__inc_ttl_by = inc_ttl_by
        self.__dec_ttl_by = dec_ttl_by

    def get_ttl_value(self) -> Optional[int]:
        """Returns the value to set the TTL to
        """
        return self.__set_ttl_to

    def get_ttl_inc(self) -> Optional[int]:
        """Returns the TTL increment value
        """
        return self.__inc_ttl_by

    def get_ttl_dec(self) -> Optional[int]:
        """Returns the TTL decrement value
        """
        return self.__dec_ttl_by

    def set_ttl_value(self, value: int) -> None:
        """Set the TTL to ``value``
        """
        self.__set_ttl_to = value

    def dec_ttl_value(self, value: int) -> None:
        """Decrease the TTL by ``value``
        """
        self.__dec_ttl_by = value

    def inc_ttl_value(self, value: int) -> None:
        """Increase the TTL by ``value``
        """
        self.__inc_ttl_by = value

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        if (self.__set_ttl_to is None and
                self.__inc_ttl_by is None and self.__dec_ttl_by is None):
            raise IptablesError('no TTL operation specified')
        retval = super().to_iptables_args()
        if self.__set_ttl_to is not None:
            retval += ['--ttl-set', str(self.__set_ttl_to)]
        elif self.__inc_ttl_by is not None:
            retval += ['--ttl-inc', str(self.__inc_ttl_by)]
        else:
            retval += ['--ttl-dec', str(self.__dec_ttl_by)]
        return retval

    @classmethod
    def parse(cls, parser: TargetParser) -> Target:
        """Parse the TTL target options

        :meta private:
        """
        set_ttl_to = None
        inc_ttl_by = None
        dec_ttl_by = None
        field_iter = parser.get_field_iter()
        try:
            ttl_op = next(field_iter)
            if ttl_op == 'set':
                val = next(field_iter)
                if val != 'to':
                    raise IptablesParsingError(
                        f"TTL target: expected 'to', got '{val}'")
                set_ttl_to = int(next(field_iter))
            elif ttl_op == 'decrement':
                val = next(field_iter)
                if val != 'by':
                    raise IptablesParsingError(
                        f"TTL target: expected 'by', got '{val}'")
                dec_ttl_by = int(next(field_iter))
            elif ttl_op == 'increment':
                val = next(field_iter)
                if val != 'by':
                    raise IptablesParsingError(
                        f"TTL target: expected 'by', got '{val}'")
                inc_ttl_by = int(next(field_iter))
            else:
                raise IptablesParsingError(
                        f"TTL target: unexpected operation: '{ttl_op}'")
        except ValueError as valerr:
            raise IptablesParsingError(
                        f'bad TTL {ttl_op} value: {val}') from valerr
        except StopIteration as stopit:
            raise IptablesParsingError('incomplete TTL target') from stopit
        target = TtlTarget(set_ttl_to, inc_ttl_by, dec_ttl_by)
        return target


TargetParser.register_target('TTL', TtlTarget, 'TTL')
