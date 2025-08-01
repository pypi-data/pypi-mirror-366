# Copyright (c) 2021, 2022, 2023, 2024, 2025, Panagiotis Tsirigotis

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
This module contains the Target base class for implementing subclasses
for iptables target extensions.
"""

import traceback

from typing import List, Optional, Tuple, Union

from ..deps import get_logger
from ..exceptions import IptablesError
from ..parsing import RuleFieldIterator

_logger = get_logger("linuxnet.iptables.targets.target")

class Target:
    """Parent class for all targets.
    """
    def __init__(self, target_name: str, terminates: bool):
        """
        :param target_name: the name of the target
        :param terminates: if ``True``, this target terminates processing
        """
        self.__target_name = target_name
        self.__terminates = terminates

    def __str__(self):
        return f'Target({self.__target_name})'

    def is_terminating(self) -> bool:
        """Returns ``True`` if this is a terminating target
        """
        return self.__terminates

    def get_target_name(self) -> str:
        """Returns the target name
        """
        return self.__target_name

    def __eq__(self, other):
        """Target comparison is only by name.
        This implies that we do not distinguish between targets
        with the same name but different options.
        """
        return (isinstance(other, Target) and
                self.__target_name == other.get_target_name())

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        if not self.__target_name:
            return []
        return [self.__target_name]


class TargetNone(Target):       # pylint: disable=too-few-public-methods
    """A target that is not there.
    This class is intended to be used for comparison purposes.
    """
    def __init__(self):
        super().__init__("", terminates=False)

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        return []


class Targets:
    """This class provides a namespace for all target classes
    """

    #: Special ``ACCEPT`` target
    ACCEPT = Target('ACCEPT', terminates=True)

    #: Special ``DROP`` target
    DROP = Target('DROP', terminates=True)

    #: Special ``QUEUE`` target
    QUEUE = Target('QUEUE', terminates=True)

    #: Special ``RETURN`` target
    RETURN = Target('RETURN', terminates=True)

    __SPECIAL_TARGET_MAP = {
                        'ACCEPT' : ACCEPT,
                        'DROP' : DROP,
                        'QUEUE' : QUEUE,
                        'RETURN' : RETURN,
                    }

    @classmethod
    def get_special(cls, target_name: str) -> Optional[Target]:
        """Returns the :class:`Target` object for the special target
        identified by ``target_name``.

        The special targets are:

            - ``ACCEPT``
            - ``DROP``
            - ``RETURN``
            - ``QUEUE``
        """
        return cls.__SPECIAL_TARGET_MAP.get(target_name)

    @classmethod
    def from_policy(cls, policy: str) -> Target:
        """Return the :class:`Target` object for one the special targets
        that can be used as a policy target. These include:

            - ``ACCEPT``
            - ``DROP``
            - ``QUEUE``

        """
        if policy == 'ACCEPT':
            return cls.ACCEPT
        if policy == 'DROP':
            return cls.DROP
        if policy == 'QUEUE':
            return cls.QUEUE
        raise IptablesError(f"No target for policy '{policy}'")


class UnparsedTarget(Target):   # pylint: disable=too-few-public-methods
    """We use this class for targets we cannot parse.
    This allows us to process **iptables(8)** output without triggering
    parsing errors. An error will be triggered lazily if/when an
    object of this class is used to generate an **iptables(8)** command
    line.
    """
    def __init__(self, target_name: str, field_iter):
        """
        :param target_name: the target name
        :param field_iter: iterator returning fields of a line
        """
        super().__init__(target_name, terminates=False)
        self.__options = []
        for field in field_iter:
            if field == target_name:
                self.__options = list(field_iter)
                break
            field_iter.store_field(field)

    def get_target_options(self) -> List[str]:
        """Returns target options
        """
        return self.__options

    def is_terminating(self) -> bool:
        """Raises an :exc:`IptablesError` since we don't know if this
        target is terminating or not.
        """
        raise IptablesError(
                f"unknown if unparsed target {self.get_target_name()} "
                "is terminating or not")

    def to_iptables_args(self) -> List[str]:
        """Since this is an unparsed target, it cannot be expressed
        in **iptables(8)** arguments.
        """
        raise IptablesError(f'unable to parse options of {self}')


class ChainTarget(Target):
    """This class handles a target that is a chain
    """
    def __init__(self, *, chain=None,
                        real_chain_name: Optional[str] =None):
        """
        Either ``chain`` or ``real_chain_name`` must be present (and
        not ``None``).
        If both are present, the chain's real name must be equal to
        ``real_chain_name``.

        The target name is set to the real chain name.

        :param chain: a :class:`Chain` object
        :param real_chain_name: a string
        """
        if real_chain_name is not None:
            if chain is not None and chain.get_real_name() != real_chain_name:
                raise IptablesError(
                        f"chain name '{chain.get_real_name()}' does not match "
                        f"provided name '{real_chain_name}'")
            target_name = real_chain_name
        else:
            if chain is None:
                raise IptablesError(
                    'attempt to create ChainTarget without providing '
                    'chain object or chain name')
            target_name = chain.get_real_name()
        super().__init__(target_name, terminates=False)
        self.__chain = chain

    def get_chain(self) -> Optional['Chain']:
        """Returns the :class:`Chain` object
        """
        return self.__chain

    def resolve_chain(self, pft, log_failure=True) -> Optional['Chain']:
        """Resolve the target name to the :class:`Chain` object, and return
        that object.

        :param pft: the :class:`IptablesPacketFilterTable` object that is
            expected to contain the chain
        :param log_failure: if ``True`` and resolution fails, log a warning
        :rtype: a :class:`Chain` object or ``None``
        """
        if self.__chain is None:
            real_chain_name = self.get_target_name()
            self.__chain = pft.get_chain_by_rcn(real_chain_name)
            if self.__chain is None and log_failure:
                _logger.warning("%s: unable to resolve chain name %s",
                    self.resolve_chain.__qualname__, real_chain_name)
                _logger.warning("Call stack:\n%s",
                        ''.join(traceback.extract_stack().format()[:-1]))
        return self.__chain


class TargetParser:
    """This class handles target parsing
    """

    # Key: string
    # Value: tuple of (Target subclass, start_field, prefix_match)
    _target_class_map = {}

    def __init__(self, target_name: Optional[str],
                                field_iter: RuleFieldIterator,
                                *, ipv6: bool):
        """
        :param target_name: the target name
        :param field_iter: a :class:`RuleFieldIterator`
        :param ipv6: if ``True``, then we are parsing the output of
            **ip6tables(8)**
        """
        self.__target_name = target_name
        self.__iter = field_iter
        self.__ipv6 = ipv6

    def is_ipv6_output(self):
        """Returns ``True`` if parsing the output of **ip6tables(8)** output
        """
        return self.__ipv6

    def get_field_iter(self) -> RuleFieldIterator:
        """Returns the :class:`RuleFieldIterator` instance that iterates
        over the fields of the rule.
        """
        return self.__iter

    @classmethod
    def register_target(cls, target_name:str, target_klass,
                        start_field: Optional[Union[str, Tuple]] =None,
                        prefix_match: Optional[bool] =False):
        """Register a class to handle parsing for a target.

        :param target_name: this is the target name that appears in the
            ``iptables -L`` output.
        :param target_klass: a subclass of :class:`Target`
        :param start_field: the field in the **iptables(8)** output that
            is the beginning of the target fields; if present, the iterator
            passed to :meth:`parse` of the ``target_class`` will be
            forwarded past the field that matches ``start_field``;
            ``start_field`` may also be specified as tuple of field names
        :param prefix_match: if ``True``, ``start_field`` is the prefix
            of the field that is the beginning of the target fields
        """
        cls._target_class_map[target_name] = (target_klass,
                                                start_field, prefix_match)

    def parse_target(self, is_goto: bool) -> Optional[Target]:
        """Parses the specified target name and options.
        Returns a (subclass of) :class:`Target`,
        or ``None`` if there is no target name.
        """
        target_name = self.__target_name
        field_iter = self.__iter
        #
        # 1. No target name
        #
        if target_name is None:
            field_iter.store_rest()
            return None
        #
        # 2. Potential chain target: either goto, or target name is not
        #    all upper-case
        #
        if is_goto:
            field_iter.store_rest()
            return ChainTarget(real_chain_name=target_name)
        if not target_name.isupper():
            field_iter.store_rest()
            return ChainTarget(real_chain_name=target_name)
        #
        # 3. Special target
        #
        target = Targets.get_special(target_name)
        if target is not None:
            field_iter.store_rest()
            return target
        #
        # 4. Target extension
        #
        tupval = self._target_class_map.get(target_name)
        if tupval is not None:
            klass, start_field, prefix_match = tupval
            # NB: will only advance if start_field is not None
            field_iter.forward(start_field, prefix_match=prefix_match)
            return klass.parse(self)
        #
        # 5. Unparsed
        #
        return UnparsedTarget(target_name, field_iter)
