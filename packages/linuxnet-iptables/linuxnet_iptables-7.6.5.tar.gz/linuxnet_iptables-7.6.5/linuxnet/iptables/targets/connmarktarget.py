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
This module provides the ConnmarkTarget class which provides access to
the iptables CONNMARK target.
"""

from typing import List, Optional

from ..deps import get_logger
from ..exceptions import IptablesParsingError, IptablesError

from .target import Target, TargetParser
from .marktarget import _MarkOperations

_logger = get_logger("linuxnet.iptables.target.connmarktarget")


class ConnmarkTarget(_MarkOperations, Target):
    """This class provides access to the ``CONNMARK`` target
    """
    def __init__(self, *, mark: Optional[int] =None,
                        restore_mark=False,
                        save_mark=False,
                        nfmask: Optional[int] =None,
                        ctmask: Optional[int] =None):
        """
        :param mark: value used to set the ctmark value (associated with
            a connection)
        :param restore_mark: if ``True``, copy the connection mark to the
            packet mark
        :param save_mark: if ``True``, copy the packet mark to the
            connection mark
        :param nfmask: applies to the save/restore operation
            (see **iptables(8)**); defaults to ``0xffffffff`` if not present
        :param ctmask: applies to the save/restore operation
            (see **iptables(8)**); defaults to ``0xffffffff`` if not present
        """
        super().__init__('CONNMARK', terminates=False)
        self.__save_mark = False
        self.__restore_mark = False
        self.__nfmask = self.NOMASK
        self.__ctmask = self.NOMASK
        if int(mark is not None) + int(restore_mark) + int(save_mark) > 1:
            raise IptablesError('can either set, save, or restore mark')
        if mark is not None:
            self.set_mark(mark)
        elif restore_mark or save_mark:
            self.__restore_mark = restore_mark
            self.__save_mark = save_mark
            if nfmask is not None:
                self.__nfmask = nfmask
            if ctmask is not None:
                self.__ctmask = ctmask

    def _assert_no_action(self) -> None:
        """Raise an IptablesError is an action has already been specified.
        """
        if self.__restore_mark:
            raise IptablesError('restore action present')
        if self.__save_mark:
            raise IptablesError('save action present')
        super()._assert_no_action()

    def is_restoring_mark(self) -> bool:
        """Returns ``True`` if this target object is set to restore the
        mark, i.e. copy the connection mark to the packet mark
        """
        return self.__restore_mark

    def is_saving_mark(self) -> bool:
        """Returns ``True`` if this target object is set to save the
        mark, i.e. copy the packet mark to the connection mark
        """
        return self.__save_mark

    def restore_mark(self, *,
                        nfmask: Optional[int] =None,
                        ctmask: Optional[int] =None) -> None:
        """Sets this target object to restore the mark.

        :param nfmask: defaults to ``0xffffffff`` if not present
        :param ctmask: defaults to ``0xffffffff`` if not present
        """
        self._assert_no_action()
        self.__restore_mark = True
        self.__nfmask = nfmask if nfmask is not None else self.NOMASK
        self.__ctmask = ctmask if ctmask is not None else self.NOMASK

    def save_mark(self, *,
                        nfmask: Optional[int] =None,
                        ctmask: Optional[int] =None) -> None:
        """Sets this target object to save the mark.

        :param nfmask: defaults to ``0xffffffff`` if not present
        :param ctmask: defaults to ``0xffffffff`` if not present
        """
        self._assert_no_action()
        self.__save_mark = True
        self.__nfmask = nfmask if nfmask is not None else self.NOMASK
        self.__ctmask = ctmask if ctmask is not None else self.NOMASK

    def get_nfmask(self) -> int:
        """Returns the nfmask
        """
        return self.__nfmask

    def get_ctmask(self) -> int:
        """Returns the ctmask
        """
        return self.__ctmask

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        retval = super().to_iptables_args()
        if self.__restore_mark or self.__save_mark:
            if self.__restore_mark:
                retval += ['--restore-mark']
            else:
                retval += ['--save-mark']
            if self.__nfmask != self.NOMASK:
                retval += ['--nfmask', f'0x{self.__nfmask:x}']
            if self.__ctmask != self.NOMASK:
                retval += ['--ctmask', f'0x{self.__ctmask:x}']
            return retval
        return self.mark_iptables_args(retval)

    @classmethod
    def _parse_masks(cls, field_iter: 'RuleFieldIterator'):
        """Parse the nfmask/ctmask and return a kwargs dictionary with
        possible keys 'nfmask', 'ctmask' and the corresponding values.
        """
        kwargs = {}
        for val in field_iter:
            if val == 'nfmask':
                maskstr = next(field_iter)
                if maskstr[0] == '~':
                    maskstr = maskstr[1:]
                kwargs['nfmask'] = int(maskstr, 16)
            elif val == 'ctmask':
                maskstr = next(field_iter)
                if maskstr[0] == '~':
                    maskstr = maskstr[1:]
                kwargs['ctmask'] = int(maskstr, 16)
            else:
                raise IptablesParsingError(f'unexpected CONNMARK field: {val}')
        return kwargs

    @classmethod
    def parse(cls, parser: TargetParser) -> Target:
        """Parse the CONNMARK target options::

            CONNMARK restore ctmask 0x1f nfmask ~0xfffff
            CONNMARK save nfmask 0xfffff ctmask ~0x1f
            CONNMARK xset 0x20/0xff

        :meta private:
        """
        action = None
        field_iter = parser.get_field_iter()
        target = ConnmarkTarget()
        try:
            action = next(field_iter)
            if target.parse_op(action, field_iter):
                pass
            elif action == 'restore':
                restore_kwargs = cls._parse_masks(field_iter)
                target.restore_mark(**restore_kwargs)
            elif action == 'save':
                save_kwargs = cls._parse_masks(field_iter)
                target.save_mark(**save_kwargs)
            else:
                raise IptablesParsingError(f'unknown CONNMARK action: {action}')
        except StopIteration as stopiter:
            raise IptablesParsingError(
                        'insufficient CONNMARK options') from stopiter
        return target


TargetParser.register_target('CONNMARK', ConnmarkTarget, 'CONNMARK')
