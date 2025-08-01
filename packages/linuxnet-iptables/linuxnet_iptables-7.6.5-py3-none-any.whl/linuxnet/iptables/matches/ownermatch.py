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
This module provides matching against UID/GID
"""

from typing import Iterable

from ..exceptions import IptablesParsingError
from ..deps import get_logger

from .match import Match, MatchParser
from .util import BooleanCriterion, NumberOrRangeCriterion

_logger = get_logger('linuxnet.iptables.matches.ownermatch')


class UidCriterion(NumberOrRangeCriterion):
    """Compare with a uid, or uid range
    """

    def __init__(self, match: Match):
        super().__init__(match, '--uid-owner', sep='-')


class GidCriterion(NumberOrRangeCriterion):
    """Compare with a gid, or gid range
    """

    def __init__(self, match: Match):
        super().__init__(match, '--gid-owner', sep='-')


class SocketExistsCriterion(BooleanCriterion):
    """Perform a socket existence test
    """

    def __init__(self, match: Match):
        super().__init__(match, '--socket-exists')


class SupplGroupsCriterion(BooleanCriterion):
    """Consider supplementary groups for GID match
    """

    def __init__(self, match: Match):
        super().__init__(match, '--suppl-groups', supports_negation=False)


class OwnerMatch(Match):
    """Match against userid, groupid, or socket existence.

    Only numeric userid, groupid values are supported.
    """

    def __init__(self):
        self.__uid_crit = None
        self.__gid_crit = None
        self.__socket_exists_crit = None
        self.__suppl_groups_crit = None

    @staticmethod
    def get_match_name() -> str:
        """Returns the **iptables(8)** match extension name
        """
        return 'owner'

    def get_criteria(self) -> Iterable['Criterion']:
        """Returns the owner match criteria: uid, gid, socket-exists
        """
        return (self.__uid_crit, self.__gid_crit, self.__socket_exists_crit,
                        self.__suppl_groups_crit)

    def uid(self) -> UidCriterion:
        """Compare with the UID
        """
        if self.__uid_crit is None:
            self.__uid_crit = UidCriterion(self)
        return self.__uid_crit

    def gid(self) -> GidCriterion:
        """Compare with the GID
        """
        if self.__gid_crit is None:
            self.__gid_crit = GidCriterion(self)
        return self.__gid_crit

    def socket_exists(self) -> SocketExistsCriterion:
        """Match if there is a socket for this packet
        """
        if self.__socket_exists_crit is None:
            self.__socket_exists_crit = SocketExistsCriterion(self)
        return self.__socket_exists_crit

    def suppl_groups(self) -> SupplGroupsCriterion:
        """Consider supplementary groups for gid match
        """
        if self.__suppl_groups_crit is None:
            self.__suppl_groups_crit = SupplGroupsCriterion(self)
        return self.__suppl_groups_crit

    def _parse_criteria(self,           # pylint: disable=too-many-branches
                        criteria_iter, is_equal) -> bool:
        """Parse the owner criteria.
        Returns ``False`` if the same criterion is encountered again
        (example: owner UID 10-100 ! owner UID 20)
        This is an indication of a new match.
        """
        token = next(criteria_iter)
        if token in ('UID', 'GID'):
            if token == 'UID':
                crit = self.uid()
            else:
                crit = self.gid()
            if crit.is_set():
                criteria_iter.put_back(token)
                return False
            if next(criteria_iter) != 'match':
                raise IptablesParsingError(
                    f"found token {token}; expected 'match'")
            from_num = None
            to_num = None
            num_spec = next(criteria_iter)
            if '-' in num_spec:
                numbers = num_spec.split('-', 1)
                from_num = int(numbers[0])
                to_num = int(numbers[1])
            else:
                from_num = int(num_spec)
            crit.compare(is_equal, from_num, to_num)
            if token == 'GID' and criteria_iter.peek() == 'incl.':
                # We expect the sequence 'incl. suppl. groups'
                _ = next(criteria_iter)
                token = next(criteria_iter)
                if token != 'suppl.':
                    raise IptablesParsingError(
                        f"found token {token}; expected 'suppl.'")
                token = next(criteria_iter)
                if token != 'groups':
                    raise IptablesParsingError(
                        f"found token {token}; expected 'groups'")
                self.suppl_groups().equals()
        elif token == 'socket':
            crit = self.socket_exists()
            if crit.is_set():
                criteria_iter.put_back(token)
                return False
            token = next(criteria_iter)
            if token != 'exists':
                raise IptablesParsingError(
                    f"found token {token}; expected 'exists'")
            crit.compare(is_equal)
        else:
            raise IptablesParsingError(
                    f'unexpected token {token} parsing owner match')
        return True

    @classmethod
    def parse(cls, parser: MatchParser) -> Match:
        """Parse owner; the syntax is a concatenation of a subset of
        the following forms::

            [!] owner UID|GID match <num>[-<num>]
            [!] owner socket exists

        The leading 'owner' field (and the preceding '!' if present)
        has already been consumed when this method is invoked.

        :meta private:
        """
        # Return the 'owner' field and the negation if present to the
        # iterator so that we can process them as part of the for-loop below.
        # The for-loop is designed to handle all owner-related criteria
        # (which we expect to appear consecutively).
        # Because of the rewind, this method is now responsible for handling
        # StopIteration errors.
        parser.rewind_match()
        match = OwnerMatch()
        criteria_iter = parser.get_iter()
        negation = None
        for token in criteria_iter:
            try:
                if token == '!':
                    negation = token
                    token = next(criteria_iter)
                if token != 'owner' or not match._parse_criteria(
                                            criteria_iter, negation is None):
                    criteria_iter.put_back(token)
                    if negation is not None:
                        criteria_iter.put_back(negation)
                    break
            except StopIteration as stopiter:
                if negation is not None or token is not None:
                    if token is None:
                        raise IptablesParsingError(
                            'negation without criterion') from stopiter
                    raise IptablesParsingError(
                            'incomplete owner match') from stopiter
            negation = None
            token = None
        return match


MatchParser.register_match('owner', OwnerMatch)
