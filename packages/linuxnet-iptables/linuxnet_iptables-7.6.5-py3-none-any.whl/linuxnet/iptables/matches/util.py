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
This module provides helper classes for implementing Match/Criteria
subclasses.
"""

from typing import Any, List, Optional, Tuple

from ..deps import get_logger
from ..exceptions import IptablesError

from .match import Criterion, Match

_logger = get_logger('linuxnet.iptables.matches.util')



class GenericCriterion(Criterion):
    """A helper class that can be used by all criteria that
    correspond to **iptables(8)** options of the form "[!] option value",
    for example, "[!] -p tcp"
    """

    def __init__(self, match: Match, iptables_option: str, norm=None):
        """
        :param match: the owner :class:`Match`
        :param iptables_option: the **iptables(8)** option to use when
            generating the iptables arguments
        :param norm: an optional callable that normalizes the value
            that we are comparing against
        """
        super().__init__(match)
        self.__value = None
        self.__option = iptables_option
        self.__norm = norm

    def get_iptables_option(self) -> str:
        """Returns the **iptables(8)** option
        """
        return self.__option

    def get_value(self) -> Any:
        """Returns the criterion value
        """
        return self.__value

    def equals(self, value) -> Match:    # pylint: disable=arguments-differ
        """Compare with the specified value
        """
        if self.__norm is None:
            self.__value = value
        else:
            self.__value = self.__norm(value)
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Convert to **iptables(8)** arguments
        """
        return [self.__option, str(self.__value)]


class GenericPositiveCriterion(GenericCriterion):
    """A subclass of :class:`GenericCriterion` for criteria that do
    not support negation.
    """
    def not_equals(self, *args, **kwargs):
        """Indicates that negation is not supported by raising
        an :exc:`IptablesError`
        """
        raise IptablesError(
                f'{self.get_iptables_option()} does not support negation')


class BooleanCriterion(Criterion):
    """Helper class for criteria that test single bits.
    """

    def __init__(self, match: Match, iptables_option: str,
                                        supports_negation=True):
        """
        :param match: the :class:`Match` object that owns this ``Criterion``
        :param iptables_option: the **iptables(8)** option to use for this
            criterion
        :param supports_negation: if ``True``, the criteria supports
            the meth:not_equals method
        """
        super().__init__(match)
        self.__option = iptables_option
        self.__supports_negation = supports_negation

    def get_value(self) -> bool:
        """Returns the criterion value
        """
        return self.is_positive()

    def bit_set(self) -> Match:
        """Check if the bit is set
        """
        return self.equals()

    def bit_not_set(self) -> Match:
        """Check if the bit is set
        """
        return self.not_equals()

    def equals(self) -> Match:    # pylint: disable=arguments-differ
        """Compare with the setting of the bit
        """
        return self._set_polarity(True)

    def not_equals(self) -> Match:      # pylint: disable=arguments-differ
        """Express a test against the criterion being ``False``
        """
        if not self.__supports_negation:
            raise IptablesError(
                    f'{self.__option} does not support negation')
        return super().not_equals()

    def _crit_iptables_args(self) -> List[str]:
        """Convert to **iptables(8)** arguments
        """
        return [self.__option]


class NumberOrRangeCriterion(Criterion):
    """Compare against a number or a number range
    """
    def __init__(self, match: Match, iptables_option: str, *, sep: str):
        super().__init__(match)
        self.__option = iptables_option
        self.__sep = sep
        self.__first = None
        self.__last = None

    def get_value(self) -> Tuple[int, Optional[int]]:
        """Returns the value that the criterion is comparing against

        :rtype: a tuple of (int, int|None)
        """
        return (self.__first, self.__last)

    def equals(self,                    # pylint: disable=arguments-differ
                first: int, last: Optional[int] =None) -> Match:
        """Compare with a number (or inclusion in number-range if ``last``
        is present)
        """
        self.__first = first
        self.__last = last
        return self._set_polarity(True)

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified port(s)
        """
        range_spec = str(self.__first)
        if self.__last is not None:
            range_spec += f'{self.__sep}{self.__last}'
        return [self.__option, range_spec]


class Rate:             # pylint: disable=too-few-public-methods
    """Used to express rates
    """

    def __init__(self, rate: int, interval: Optional[str] =None):
        """
        :param rate: (integer) rate value
        :param interval: optional (string) time interval (defaults to `PER_SEC`)

        Possible interval values are:
        """
        if interval is None:
            interval = self.PER_SEC
        elif interval not in (self.PER_DAY, self.PER_HOUR,
                self.PER_MINUTE, self.PER_MIN, self.PER_SECOND, self.PER_SEC):
            raise ValueError(f'bad time interval: {interval}')
        if rate <= 0:
            raise ValueError(f'bad rate: {rate}')
        self.__rate = int(rate)
        if interval == self.PER_MINUTE:
            interval = self.PER_MIN
        elif interval == self.PER_SECOND:
            interval = self.PER_SEC
        self.__interval = interval

    #: day interval
    PER_DAY = 'day'
    #: hour interval
    PER_HOUR = 'hour'
    #: minute interval
    PER_MIN = 'min'
    #: minute interval (normalized to 'min')
    PER_MINUTE = 'minute'
    #: second interval
    PER_SEC = 'sec'
    #: second interval (normalized to 'sec')
    PER_SECOND = 'second'

    def get_rate(self) -> int:
        """Returns the rate value
        """
        return self.__rate

    def get_interval(self) -> str:
        """Returns the rate interval
        """
        return self.__interval

    def __eq__(self, other):
        return (isinstance(other, Rate) and
                        self.__rate == other.get_rate() and
                            self.__interval == other.get_interval())

    @classmethod
    def str2rate(cls, spec: str) -> 'Rate':
        """Convert the ``spec`` string into a :class:`Rate` object.
        The expected format is: ``num/interval`` (e.g. ``10/min``).

        Raises a :exc:`ValueError` if ``spec`` cannot be parsed.
        """
        fields = spec.split('/')
        if len(fields) != 2:
            raise ValueError(f"bad rate spec '{spec}'")
        return cls(int(fields[0]), fields[1])

    def __str__(self):
        return f'{self.__rate}/{self.__interval}'
