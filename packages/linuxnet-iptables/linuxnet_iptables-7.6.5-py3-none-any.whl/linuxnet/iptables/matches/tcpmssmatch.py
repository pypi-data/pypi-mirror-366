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
This module supports matching against the TCP MSS
"""

from typing import Iterable, List, Optional, Tuple

from ..exceptions import IptablesError
from ..deps import get_logger

from .match import Match, Criterion, MatchParser

_logger = get_logger('linuxnet.iptables.matches.tcpmssmatch')


class MssCriterion(Criterion):
    """Compare with MSS field of the TCP header.

    The comparison value is a tuple (int, int|None) to compare against
    a specific MSS value or a range of values.
    """
    def __init__(self, match):
        super().__init__(match)
        self.__mssval = None
        self.__endval = None

    def get_value(self) -> Tuple[int, Optional[int]]:
        """Returns the value that the criterion is comparing against.

        :rtype: tuple of (int, int|None)
        """
        return (self.__mssval, self.__endval)

    def equals(self,            # pylint: disable=arguments-differ
                    mssval: int, endval: Optional[int] =None) -> Match:
        """Check for equality against ``mssval``, or range equality
        if ``endval`` is present.

        :param mssval: the MSS value
        :param endval: range of MSS values from ``mssval`` to this value
        """
        self.__mssval = mssval
        if endval is not None and endval < mssval:
            raise IptablesError('bad range: endval < mssval')
        self.__endval = endval
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the criterion
        """
        mss = f'{self.__mssval}'
        if self.__endval is not None:
            mss += f':{self.__endval}'
        return ['--mss', mss]


class TcpmssMatch(Match):
    """Match against the MSS field of the TCP header
    """
    def __init__(self):
        self.__mss_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'tcpmss'

    def get_criteria(self) -> Iterable[Criterion]:
        """Returns the TCPMSS match criteria (only one).
        """
        return (self.__mss_crit,)

    def mss(self) -> MssCriterion:
        """Match against the MSS field of the TCP header
        """
        if self.__mss_crit is None:
            self.__mss_crit = MssCriterion(self)
        return self.__mss_crit

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse tcpmss::

            tcpmss match !10:20

        'tcpmss' has already been consumed when this method
        is invoked.

        :meta private:
        """
        parser.skip_field('match')
        criteria_iter = parser.get_iter()
        is_equal, val = parser.parse_value(next(criteria_iter))
        if ':' in val:
            mstr, estr = val.split(':', 1)
            mssval = int(mstr)
            endval = int(estr)
        else:
            mssval = int(val)
            endval = None
        return TcpmssMatch().mss().compare(is_equal, mssval, endval)


MatchParser.register_match('tcpmss', TcpmssMatch)
