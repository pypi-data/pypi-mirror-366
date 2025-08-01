# Copyright (c) 2021, 2022, 2023, 2025, Panagiotis Tsirigotis

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
This module provides classes related to the parsing of the iptables output:

    - LookaheadIterator
    - RuleFieldIterator
"""

from collections import deque
from typing import Iterable, List, Optional, Tuple, Union

from .exceptions import IptablesParsingError
from .deps import get_logger


_logger = get_logger("linuxnet.iptables.parsing")


class LookaheadIterator:
    """A LookaheadIterator is an iterator that provides the ability to
    put back previously returned tokens.

    Conceptual view of the LookaheadIterator::

                               deque
       +---------------+  +---+---+---+---+---+
       | back-iterator |  | T | T | T |...| T |
       +---------------+  +---+---+---+---+---+
                                ^
                                |
                              Cursor

    * Tokens to the right of the cursor have been consumed.
    * Tokens up to, but not including, the cursor are previously consumed
      tokens that have been put back.
    * New tokens are obtained from the back-iterator.
    * The value of the cursor indicates the number of put-back tokens.
    * The maximum size of the deque is equal to the lookahead.
    """
    def __init__(self, iterable, lookahead: int):
        """
        :param iterable: an iterable object from which we create
            the back-iterator
        :param lookahead: number of tokens of look ahead
        """
        self.__iter = iter(iterable)
        if lookahead <= 0:
            raise ValueError(f'bad lookahead value {lookahead}')
        self.__tokens = deque(maxlen=lookahead)
        self.__cursor = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.__cursor == 0:
            token = next(self.__iter)
            self.__tokens.appendleft(token)
        else:
            self.__cursor -= 1
            token = self.__tokens[self.__cursor]
        return token

    def peek(self) -> Optional[str]:
        """Returns the next token, but does not consume it
        """
        try:
            token = self.__next__()
            self.put_back(token)
            return token
        except StopIteration:
            return None

    def put_back(self, token: str, *, replace_token=False) -> None:
        """This method puts the previously returned token back to the
        iterator, so that the token can be returned again.

        :param token: the token to put back to the iterator; when
            ``replace_token`` is ``False``, this must be **the** token
            previously returned by the iterator: identity is checked,
            not equality
        :param replace_token: if ``True``, it allows ``token`` to be different
            than then one previously returned by the iterator
        """
        if self.__cursor == len(self.__tokens):
            # Either there are no consumed tokens, or this is an attempt to
            # put back one more tokens than those already consumed.
            raise ValueError('not a consumed token')
        if token is not self.__tokens[self.__cursor]:
            if not replace_token:
                raise ValueError(
                    f'wrong token: expected={self.__tokens[self.__cursor]}, '
                    f'putback={token}')
            self.__tokens[self.__cursor] = token
        self.__cursor += 1

    def rewind(self, step=1) -> 'LookaheadIterator':
        """Put back last ``step`` tokens

        A :exc:`ValueError` will be raised if there are not enough
        tokens to put back.
        """
        avail = len(self.__tokens) - self.__cursor
        if step > avail:
            raise ValueError(f'unable to rewind {step} token(s)')
        self.__cursor += step
        return self


class RuleFieldIterator(LookaheadIterator):
    """
    This iterator is used to parse the target-related fields of a rule.
    When instantiated, the iterator may still be 'inside' the match
    fields due to encountering an unsupported match.

    The target-specific parsing code should advance the iterator
    until it finds the beginning of the target-related fields.
    The methods :meth:`forward` and :meth:`forward_to` may be used for this.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__stored_fields = []

    def next_field(self, attr: Optional[str] =None) -> str:
        """Returns the next field which holds the value for ``attr``

        Raises an :exc:`IptablesParsingError` if the iterator has run
        out of fields.
        """
        try:
            return next(self)
        except StopIteration as stopit:
            if attr is not None:
                raise IptablesParsingError(
                        f"missing value for '{attr}'") from stopit
            raise IptablesParsingError('no more fields') from stopit

    def forward(self, field_name: Optional[Union[str,Tuple]], *,
                prefix_match: Optional[bool] =False) -> 'RuleFieldIterator':
        """Forward past the field identified by ``field_name``, i.e.
        the next field to be returned by the iterator will be the
        one after ``field_name``.

        :param field_name: the name of field to reach; if ``None``,
             this method call is a no-op
        :param prefix_match: if ``True``, match the first field with
             a ``field_name`` prefix

        :rtype: this object

        Raises an :exc:`IptablesParsingError` if no match is found.
        """
        if field_name is None:
            return self
        try:
            while True:
                field = next(self)
                if prefix_match:
                    if field.startswith(field_name):
                        return self
                elif isinstance(field_name, tuple) and field in field_name:
                    return self
                elif field == field_name:
                    return self
                self.__stored_fields.append(field)
        except StopIteration as stopit:
            raise IptablesParsingError(
                        f"missing '{field_name}'") from stopit

    def forward_to(self, fields: Iterable[str]) -> Optional[str]:
        """Forward to a field among those in ``fields``; this
        field will be returned, if found. The next field returned by
        the iterator will be the one found.

        :param fields: field to match; if ``None`` or empty,
             this method call is a no-op

        :rtype: the matching field, or ``None``
        """
        if not fields:
            return None
        try:
            while True:
                field = next(self)
                if field in fields:
                    return field
                self.__stored_fields.append(field)
        except StopIteration:
            return None

    def next_value(self, attr: str) -> str:
        """Returns the next field which holds the value for ``attr``
        """
        try:
            return next(self)
        except StopIteration as stopit:
            raise IptablesParsingError(
                        f"missing value for '{attr}'") from stopit

    def store_field(self, field: str) -> None:
        """Store the specified field.

        Target subclasses that choose to do their own forwarding
        to find the field that starts the target options
        (instead of using the :meth:`forward` method)
        should invoke this method to 'store' the fields they skip.
        """
        self.__stored_fields.append(field)

    def store_rest(self) -> None:
        """Store any remaining fields

        :meta private:
        """
        self.__stored_fields.extend(self)

    def get_stored_fields(self) -> List[str]:
        """Returns any stored fields

        :meta private:
        """
        return self.__stored_fields
