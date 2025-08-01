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
This module contains the base classes for implementing match-specific
subclasses:
        - Match
        - Criterion

A class derived from Match (with the exception of PacketMatch) corresponds
to an iptables(8) extension match module, with the options of that module
mapping to Criterion subclasses.
The PacketMatch class is also derived from Match and offers matching
against the common criteria (source/dest address etc.)
"""

from typing import Any, Iterable, List, Optional, Tuple

from ..exceptions import IptablesError, IptablesParsingError
from ..deps import get_logger
from ..parsing import LookaheadIterator

_logger = get_logger('linuxnet.iptables.matches.match')


class Criterion:
    """
    This class is used to *express* an **iptables(8)** match criterion;
    it does not perform any comparisons.

    :class:`Criterion` is a superclass that serves the following purposes:
        1) it provides an :meth:`equals` method and a :meth:`not_equals`
           method to express a ``==`` or a ``!=`` comparison against a value
        2) it keeps track of whether the criterion has been set;
           a criterion is set when either the :meth:`equals` or
           :meth:`not_equals` method is invoked; **a criterion may only**
           **be set once**
        3) it keeps track of whether a criterion is negated or not;
           this is the criterion's **polarity** (a criterion that
           performs a ``!=`` comparison has negative polarity)
        4) it provides a :meth:`to_iptables_args` method to generate the
           ``!`` (negation) **iptables(8)** argument, and to also check
           if the criterion was set

    The :meth:`equals`/:meth:`not_equals` methods of :class:`Criterion`
    subclasses **must** invoke the :meth:`_set_polarity` method of
    :class:`Criterion` to indicate the polarity of the test.
    These methods are also responsible for saving the comparison value
    in the subclass object.

    A :class:`Criterion` has an owner which is an object of a subclass
    of :class:`Match`. The :meth:`equals`/:meth:`not_equals` methods return
    this object to facilitate building a criteria list:

    ::

        pkt_match.protocol().equals('tcp').input_interface().equals('eth0')

    """
    def __init__(self, match: 'Match'):
        """
        :param match: the :class:`Match` object that owns this ``Criterion``
        """
        self.__match: 'Match' = match
        self.__positive = None
        self._any = False

    def __eq__(self, other: 'Criterion') -> bool:
        """Returns ``True`` iff:

             * both criteria are of the same type
             * both criteria are set or both criteria are not set
             * if both criteria are set, they have the same polarity,
               and the same value
        """
        if not isinstance(other, type(self)):
            return False
        if self.is_set() ^ other.is_set():
            # One set, the other not set, so not equal
            return False
        if not self.is_set():
            # None set, so equal
            return True
        # Both set, so compare boolean values
        if self._any or other._any:
            return True
        return (self.is_positive() == other.is_positive() and
                                self.get_value() == other.get_value())

    def __ne__(self, other: 'Criterion'):
        return not self.__eq__(other)

    def is_set(self) -> bool:
        """Returns ``True`` if the criterion has been set
        """
        return self.__positive is not None

    def is_positive(self) -> bool:
        """Returns the 'polarity' of the criterion: ``True`` for
        :meth:`equals` or ``False`` for :meth:`not_equals`

        Raises :class:`IptablesError` if the criterion is not set
        """
        if not self.is_set():
            raise IptablesError('criterion not set')
        return self.__positive

    def _may_be_equal(self, other: 'Criterion') -> bool:
        """This is a helper method for derived classes that choose
        to implement the __eq__ operator.

        Returns ``True`` iff:

             *  both criteria are set or both criteria are not set
             *  if both criteria are set, they have the same polarity
        """
        if self.is_set() ^ other.is_set():
            return False
        if self.is_set():
            # Both set, so compare boolean values
            return self.is_positive() == other.is_positive()
        # None set, so equal
        return True

    def get_value(self) -> Any:
        """Returns the value that this criterion is comparing against
        """
        raise NotImplementedError

    def _set_polarity(self, polarity: bool) -> 'Match':
        """Set the comparison polarity:

            - ``True`` : equality test
            - ``False`` : inequality test

        Raises an :class:`IptablesError` if the polarity is already set.

        Returns this object.
        """
        if self.__positive is not None:
            raise IptablesError(f"attempt to modify {self.__class__.__name__}")
        self.__positive = polarity
        return self.__match

    def any(self) -> 'Match':
        """Match any value.

        This method is used when creating a :class:`Criterion` in order
        to search an existing chain for rules that try to match against
        certain packet properties (e.g. input interface) without being
        particular about the specific property value (e.g. ``eth0``).
        """
        self._any = True
        return self._set_polarity(True)

    def equals(self, *args, **kwargs) -> 'Match':
        """Express equality comparison against the argument values.

        Subclasses will implement this method to express comparisons
        against a specific value (or values). These values will be the
        arguments of the subclass method and will be stored in the
        subclass object.

        Subclasses overriding this method should invoke the
        :meth:`_set_polarity` method of this class to set the polarity
        to ``True``.

        Returns this :class:`Match` object.
        """
        raise NotImplementedError

    def not_equals(self, *args, **kwargs) -> 'Match':
        """Express inequality comparison against the argument values.

        The arguments of this method are the same as those of
        the :meth:`equals` method.

        This method invokes the :meth:`equals` method and then reverses
        the polarity.

        Returns this :class:`Match` object.
        """
        #
        # The implementation of this method works as-is and normally
        # subclasses should not need to override it.
        #
        # Subclasses overriding this method should invoke the
        # :meth:`_set_polarity` method of this class to set the polarity
        # to ``False``.
        #
        _ = self.equals(*args, **kwargs)
        self.__positive = False
        return self.__match

    def compare(self, is_equal: bool, *args, **kwargs) -> 'Match':
        """Alternative method used for comparisons. It invokes
        :meth:`equals` (or :meth:`not_equals`) with ``args`` and ``kwargs``
        if ``is_equal`` is ``True`` (or ``False``).
        """
        if is_equal:            # pylint: disable=no-else-return
            return self.equals(*args, **kwargs)
        else:
            return self.not_equals(*args, **kwargs)

    def _crit_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments for the criterion,
        except for polarity.

        **Subclasses must implement this method.**
        """
        raise NotImplementedError

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments

        This method should be invoked only for criteria that are set,
        i.e. the caller is expected to check with :meth:`Criterion.is_set`
        prior to invoking this method.

        :meta private:
        """
        if self._any:
            raise IptablesError(
                f'{self.__class__.__name__} has value set to ANY')
        retval = [] if self.is_positive() else ['!']
        retval += self._crit_iptables_args()
        return retval


class Match:
    """Parent class for all match-specific subclasses.
    """

    def get_match_name(self) -> Optional[str]:
        """Returns the **iptables(8)** match extension name
        """
        raise NotImplementedError

    def get_criteria(self) -> Iterable[Optional[Criterion]]:
        """Returns an iterable containing instances of
        :class:`Criterion` subclasses, or ``None`` values.
        """
        raise NotImplementedError

    def has_criteria(self) -> bool:
        """Returns ``True`` if the match has any criteria set
        """
        for crit in self.get_criteria():
            if crit is not None and crit.is_set():
                return True
        return False

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments for the match
        and its criteria. If no criteria are set, an empty list is
        returned.
        """
        args = []
        for crit in self.get_criteria():
            if crit is not None and crit.is_set():
                args += crit.to_iptables_args()
        if not args:
            return args
        match_name = self.get_match_name()
        if not match_name:
            return args
        return ['-m', match_name] + args

    def __eq__(self, other: 'Match'):
        """We rely on subclasses to define equality by value
        """
        if not isinstance(other, type(self)):
            return False
        for s_crit, o_crit in zip(self.get_criteria(),
                                            other.get_criteria()):
            s_crit_set = s_crit is not None and s_crit.is_set()
            o_crit_set = o_crit is not None and o_crit.is_set()
            if not s_crit_set:
                if o_crit_set:
                    return False
                continue
            if not o_crit_set:
                return False
            if s_crit != o_crit:
                return False
        return True

    def __ne__(self, other: 'Match'):
        return not self.__eq__(other)


class MatchNone(Match):
    """This is a special class to indicate the absence of any
    :class:`Match` objects.
    This class is intended to be used for comparison purposes.
    """

    @staticmethod
    def get_match_name() -> Optional[str]:
        """There is no name for :class:`MatchNone`
        """
        return None

    @staticmethod
    def get_criteria() -> Iterable[Criterion]:
        """:class:`MatchNone` has no criteria.
        """
        return tuple()

    def to_iptables_args(self) -> List[str]:
        """:class:`MatchNone` is not a real **iptables(8)** match extension,
        so invoking this method raises an :exc:`IptablesError`
        """
        raise IptablesError("MatchNone is not a real match")



class CriteriaExhaustedError(Exception):
    """Exception raised to indicate that criteria parsing has completed
    """


class MatchParser:
    """This class handles match parsing
    """

    # Key: string
    # Value: Match subclass
    _match_class_map = {}

    def __init__(self, field_iter: LookaheadIterator, *, ipv6: bool):
        """
        :param field_iter: a :class:`RuleFieldIterator` that iterates
            over the fields of the rule
        :param ipv6: if ``True``, then we are parsing the output of
            **ip6tables(8)**
        """
        self.__iter = field_iter
        self.__ipv6 = ipv6
        self.__match_name = None
        self.__negation = None

    def is_ipv6_output(self):
        """Returns ``True`` if parsing the output of **ip6tables(8)** output
        """
        return self.__ipv6

    def get_iter(self) -> LookaheadIterator:
        """Returns the field iterator
        """
        return self.__iter

    def get_match_name(self) -> Optional[str]:
        """Returns the match name, if any
        """
        return self.__match_name

    def get_negation(self) -> Optional[str]:
        """Returns the negation string, if any
        """
        return self.__negation

    @staticmethod
    def parse_value(value: str) -> Tuple[bool, str]:
        """Check if the specified value starts with '!' indicating negation.
        Returns the tuple (is_negative, value) where the optional '!'
        has been stripped from the argument 'value'
        """
        is_equal = True
        if value[0] == '!':
            is_equal = False
            value = value[1:]
        return is_equal, value

    def parse_next_value(self) -> Tuple[bool, str]:
        """Parse the next value from the iterator.
        Allow for the following syntax::

            ! value  (2 fields)
            !value (1 field)

        Returns the tuple (is_negative, value)
        """
        value = next(self.__iter)
        if value == '!':
            return False, next(self.__iter)
        return self.parse_value(value)

    def skip_field(self, expected: str):
        """Skip the next field, if it is equal to ``expected``.
        Otherwise, raise an :exc:`IptablesParsingError` exception.
        """
        val = next(self.__iter)
        if val != expected:
            _logger.error("parsing '%s': expected '%s'; found '%s'",
                self.__match_name, expected, val)
            raise IptablesParsingError(f"missing '{expected}' field")

    def rewind_match(self):
        """Returns the match name, and negation string if any,
        back to the iterator.
        """
        if self.__match_name is None:
            raise IptablesParsingError('attempt to rewind with no match')
        self.__iter.put_back(self.__match_name)
        self.__match_name = None
        if self.__negation is not None:
            self.__iter.put_back(self.__negation)
            self.__negation = None

    def parse_matches(self) -> List[Match]:
        """This method traverses the match part of the rule
        invoking the match-specific classes based on the
        name of the match.
        """
        match_list = []
        try:
            for token in self.__iter:
                #
                # Newer iptables versions have the '!' as a standalone field
                # instead of as a prefix of the value.
                #
                if token == '!':
                    self.__negation = token
                    self.__match_name = next(self.__iter)
                elif token.startswith('!'):
                    self.__negation = token[0]
                    self.__match_name = token[1:]
                else:
                    self.__match_name = token
                match = None
                klass = self._match_class_map.get(self.__match_name)
                if klass is not None:
                    try:
                        match = klass.parse(self)
                    except CriteriaExhaustedError:
                        pass
                if match is None:
                    # We don't know if it is a match criterion that we don't
                    # know about, a target name, or a target option.
                    # Let the caller figure it out.
                    self.__iter.put_back(self.__match_name)
                    self.__match_name = None
                    if self.__negation is not None:
                        self.__iter.put_back(self.__negation)
                        self.__negation = None
                    break
                match_list.append(match)
                self.__match_name = None
                self.__negation = None
        except StopIteration as stopiter:
            if self.__match_name is not None:
                raise IptablesParsingError(
                    'insufficient number of values for '
                    f'match {self.__match_name}') from stopiter
        return match_list

    @classmethod
    def register_match(cls, ident:str, klass) -> None:
        """Register the given class (which should be a subclass of
        the :class:`Match` class).
        The ``ident`` string is the match name that appears in the
        ``iptables -L`` output.
        """
        cls._match_class_map[ident] = klass
