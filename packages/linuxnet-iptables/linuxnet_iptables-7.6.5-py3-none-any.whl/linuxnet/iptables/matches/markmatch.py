# Copyright (c) 2021, 2022, 2023, Panagiotis Tsirigotis

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
This module supports matching against the FW mark
"""

from typing import Iterable, List, Optional, Tuple

from ..exceptions import IptablesError
from ..deps import get_logger

from .match import Match, Criterion, MatchParser

_logger = get_logger('linuxnet.iptables.matches.markmatch')


class MarkCriterion(Criterion):
    """A criterion for a mark, used by :class:`MarkMatch` and
    :class:`ConnmarkMatch`
    since the **iptables(8)** option used by the mark/connmark modules is
    the same.

    The comparison value is a tuple consisting of an (integer) mark value
    and an integer mask value (``None`` in case of no mask).
    """
    def __init__(self, match: Match):
        super().__init__(match)
        self.__mark = None
        self.__mask = None

    def get_value(self) -> Tuple[int, Optional[int]]:
        """Returns the value that the criterion is comparing against.

        :rtype: tuple of (int, int|None)
        """
        return (self.__mark, self.__mask)

    def equals(self,            # pylint: disable=arguments-differ
                    mark: int, mask: Optional[int] =None) -> Match:
        """Check for equality against ``mark`` and optionally ``mask``

        :param mark: the mark value
        :param mask: the mask value
        """
        if mark is None:
            raise IptablesError('mark is None')
        self.__mark = mark
        self.__mask = mask
        return self._set_polarity(True)

    def __mark2str(self):
        """Convert the mark/mask to a string; both values will be in hex
        """
        markstr = f'{self.__mark:#x}'
        if self.__mask is not None:
            markstr += f'/{self.__mask:#x}'
        return markstr

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified mark
        """
        return ['--mark', self.__mark2str()]


class MarkMatch(Match):
    """Match against the fwmark
    """
    def __init__(self):
        self.__mark_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'mark'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the mark match criteria (only one).
        """
        return (self.__mark_crit,)

    def mark(self) -> MarkCriterion:
        """Match against the packet's fwmark.
        """
        if self.__mark_crit is None:
            self.__mark_crit = MarkCriterion(self)
        return self.__mark_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse the mark criteria::

            mark match [!]<num>[/<num>]

        The 'mark' field has already been consumed.

        :meta private:
        """
        parser.skip_field('match')
        is_equal, val = parser.parse_next_value()
        mask = None
        if '/' in val:
            valstr, maskstr = val.split('/', 1)
            value = int(valstr, 16)
            mask = int(maskstr, 16)
        else:
            value = int(val, 16)
        return MarkMatch().mark().compare(is_equal, value, mask)


MatchParser.register_match('mark', MarkMatch)
