# Copyright (c) 2023, Panagiotis Tsirigotis

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
This module provides access to the ``recent`` match
"""

from enum import Enum
from ipaddress import IPv4Address
from typing import Iterable, List, Optional

from ..deps import get_logger
from ..exceptions import IptablesError, IptablesParsingError

from .match import Criterion, Match, MatchParser
from .util import GenericPositiveCriterion, BooleanCriterion

_logger = get_logger('linuxnet.iptables.matches.recentmatch')


class RecentMatchAction(Enum):
    """Actions for the ``recent`` match. The value of each is
    the corresponding iptables option.
    """
    #: SET action
    SET = "--set"
    #: UPDATE action
    UPDATE = "--update"
    #: CHECK action
    CHECK = "--rcheck"
    #: REMOVE action
    REMOVE = "--remove"


class ActionCriterion(Criterion):
    """Specify the action to take
    """

    def __init__(self, match: Match):
        super().__init__(match)
        self.__action = None

    def get_value(self) -> RecentMatchAction:
        """Returns the action
        """
        return self.__action

    def equals(self,                    # pylint: disable=arguments-differ
            action: RecentMatchAction, *, match_if_found=True) -> Match:
        """
        :param action: identifies the action to take
        :param match_if_found: if ``False``, when the packet address
            is present in the identified list, the ``recent`` match will
            cause the rule to **fail** to match the packet
        """
        self.__action = action
        return self._set_polarity(match_if_found)

    def not_equals(self, *args, **kwargs):
        """This criterion does not support inequality testing.
        This method will raise an :exc:`IptablesError`
        """
        raise IptablesError("criterion does not support negation")

    def _crit_iptables_args(self) -> List[str]:
        return [self.__action.value]


class AddressSelection(Enum):
    """Identify whether we are comparing against the packet's source or
    destination address
    """
    #: select packet source address
    SOURCE_ADDRESS = '--rsource'
    #: select packet destination address
    DEST_ADDRESS = '--rdest'


class AddressSelectionCriterion(Criterion):
    """Compare against the packet's source or destination address
    """
    def __init__(self, match: Match):
        super().__init__(match)
        self.__selection = None

    def get_value(self) -> AddressSelection:
        """Returns the value of the criterion (identification of which
        packet address is selected)
        """
        return self.__selection

    def equals(self,                    # pylint: disable=arguments-differ
                        selection: AddressSelection) -> Match:
        self.__selection = selection
        return self._set_polarity(True)

    def not_equals(self, *args, **kwargs):
        """This criterion does not support inequality comparison.
        This method raises an :exc:`IptablesError`
        """
        raise IptablesError("inequality comparison not supported")

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified selection.
        """
        if self.__selection is not None:
            return [self.__selection.value]
        return []


class MaskCriterion(Criterion):
    """Apply the specified mask.

    The value is an :class:`IPv4Address`.
    """

    SKIP_MASK = IPv4Address('255.255.255.255')

    def __init__(self, match: Match):
        super().__init__(match)
        self.__mask = None

    def get_value(self) -> Optional[IPv4Address]:
        """Returns the mask
        """
        return self.__mask

    def equals(self, mask) -> Match:    # pylint: disable=arguments-differ
        """Use the specified source mask
        """
        self.__mask = mask
        self._set_polarity(True)

    def not_equals(self, *args, **kwargs):
        """This :class:`Criterion` method is not supported
        """
        raise IptablesError('method not_equals() not supported')

    def _crit_iptables_args(self) -> List[str]:
        """Returns **iptables(8)** arguments for the specified rate
        """
        if self.__mask == self.SKIP_MASK:
            return []
        return ['--mask', str(self.__mask)]



class RecentMatch(Match):
    """Match against list of IP addresses.
    """

    #: SET action
    SET = RecentMatchAction.SET
    #: UPDATE action
    UPDATE = RecentMatchAction.UPDATE
    #: CHECK action
    CHECK = RecentMatchAction.CHECK
    #: REMOVE action
    REMOVE = RecentMatchAction.REMOVE

    #: select packet source address
    SOURCE_ADDRESS = AddressSelection.SOURCE_ADDRESS
    #: select packet destination address
    DEST_ADDRESS = AddressSelection.DEST_ADDRESS

    def __init__(self):
        self.__action_crit = None
        self.__name_crit = None
        self.__seconds_crit = None
        self.__hitcount_crit = None
        self.__same_ttl_crit = None
        self.__address_selection_crit = None
        self.__reap_crit = None
        self.__mask_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'recent'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the recent match criteria.
        """
        # We create a temporary AddressSelectionCriterion with
        # the default match behavior.
        address_selection_crit = self.__address_selection_crit
        if address_selection_crit is None:
            address_selection_crit = AddressSelectionCriterion(self)
            address_selection_crit.equals(self.SOURCE_ADDRESS)
        # We create a temporary MaskCritetion with the default mask
        mask_crit = self.__mask_crit
        if mask_crit is None:
            mask_crit = MaskCriterion(self)
            mask_crit.equals(MaskCriterion.SKIP_MASK)
        return (self.__action_crit, self.__name_crit, self.__seconds_crit,
            self.__hitcount_crit, self.__same_ttl_crit, address_selection_crit,
            self.__reap_crit, mask_crit)

    def name(self) -> GenericPositiveCriterion:
        """Identify the list name
        """
        if self.__name_crit is None:
            self.__name_crit = GenericPositiveCriterion(self, '--name')
        return self.__name_crit

    def action(self) -> ActionCriterion:
        """Identify the action
        """
        if self.__action_crit is None:
            self.__action_crit = ActionCriterion(self)
        return self.__action_crit

    def address_selection(self) -> AddressSelectionCriterion:
        """Identify the address selection
        """
        if self.__address_selection_crit is None:
            self.__address_selection_crit = AddressSelectionCriterion(self)
        return self.__address_selection_crit

    def seconds(self) -> GenericPositiveCriterion:
        """Specify number of seconds
        """
        if self.__seconds_crit is None:
            self.__seconds_crit = GenericPositiveCriterion(self, '--seconds')
        return self.__seconds_crit

    def hitcount(self) -> GenericPositiveCriterion:
        """Specify a hitcount
        """
        if self.__hitcount_crit is None:
            self.__hitcount_crit = GenericPositiveCriterion(self, '--hitcount')
        return self.__hitcount_crit

    def same_ttl(self) -> BooleanCriterion:
        """Specify same-TTL comparison.
        """
        if self.__same_ttl_crit is None:
            self.__same_ttl_crit = BooleanCriterion(self, "--rttl",
                                                supports_negation=False)
        return self.__same_ttl_crit

    def reap(self) -> BooleanCriterion:
        """Specify old address reaping
        """
        if self.__reap_crit is None:
            self.__reap_crit = BooleanCriterion(self, "--reap",
                                                supports_negation=False)
        return self.__reap_crit

    def mask(self) -> MaskCriterion:
        """Specify a source mask
        """
        if self.__mask_crit is None:
            self.__mask_crit = MaskCriterion(self)
        return self.__mask_crit

    # pylint: disable=too-many-branches
    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Possible output::

        recent: CHECK TTL-Match name: foobar side: source LOG flags 0 level 4
        !recent: SET name: foobar side: source LOG flags 0 level 4
        !recent: UPDATE seconds: 4 hit_count: 3 name: foobar side: source
        recent: REMOVE name: foobar side: dest/* silly */ LOG flags 0 level 4

        The 'recent' part is already consumed. The parser has also recorded
        if there was a '!' present.
        Note the output bug when the value of 'side:' is 'dest'.
        We look for this and put-back the rest of the string.

        :meta private:
        """
        criteria_iter = parser.get_iter()
        match_if_found = parser.get_negation() is None
        match = RecentMatch()
        #
        # The action is always present at the beginning
        #
        actionstr = next(criteria_iter)
        if actionstr == 'CHECK':
            match.action().equals(cls.CHECK, match_if_found=match_if_found)
        elif actionstr == 'SET':
            match.action().equals(cls.SET, match_if_found=match_if_found)
        elif actionstr == 'UPDATE':
            match.action().equals(cls.UPDATE, match_if_found=match_if_found)
        elif actionstr == 'REMOVE':
            match.action().equals(cls.REMOVE, match_if_found=match_if_found)
        else:
            raise IptablesParsingError(
                        f'recent match unexpected action: {actionstr}')
        for val in criteria_iter:
            if val == 'TTL-Match':
                match.same_ttl().equals()
            elif val == 'name:':
                match.name().equals(next(criteria_iter))
            elif val == 'hit_count:':
                match.hitcount().equals(int(next(criteria_iter)))
            elif val == 'seconds:':
                match.seconds().equals(int(next(criteria_iter)))
            elif val == 'side:':
                address_selection = next(criteria_iter)
                if address_selection == 'source':
                    match.address_selection().equals(cls.SOURCE_ADDRESS)
                elif address_selection.startswith('dest'):
                    match.address_selection().equals(cls.DEST_ADDRESS)
                    rest = address_selection[4:]
                    if rest:
                        criteria_iter.put_back(rest, replace_token=True)
            elif val == 'reap':
                match.reap().equals()
            elif val == 'mask:':
                match.mask().equals(IPv4Address(next(criteria_iter)))
            else:
                criteria_iter.put_back(val)
                break
        return match
    # pylint: enable=too-many-branches


MatchParser.register_match('recent:', RecentMatch)
