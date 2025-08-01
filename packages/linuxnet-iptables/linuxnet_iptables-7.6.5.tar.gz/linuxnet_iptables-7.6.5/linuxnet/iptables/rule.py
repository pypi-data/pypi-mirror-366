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

"""This module provides the ChainRule class
"""

from typing import Iterator, List, Optional

from .exceptions import IptablesError, IptablesParsingError
from .matches import Match, MatchNone, PacketMatch, CommentMatch
from .matches.match import MatchParser
from .parsing import LookaheadIterator, RuleFieldIterator
from .targets import Target, ChainTarget, UnparsedTarget, TargetNone
from .targets.target import TargetParser
from .deps import get_logger


_logger = get_logger("linuxnet.iptables.rule")


class ChainRule:        # pylint: disable=too-many-instance-attributes
    """This class represents a rule in an **iptables(8)** chain.
    A :class:`ChainRule` has a (possibly empty) list of :class:`Match`
    objects and an optional :class:`Target` object.

    Multiple :class:`Match` objects of the same type can be included
    in a rule. Since multiple :class:`Match` objects imply a logical-AND,
    including objects of the same type may be useful when using negation.
    However, there can be at most one :class:`PacketMatch` object included.

    A :class:`ChainRule` object is iterable, returning the rule's
    :class:`Match` instances.
    """

    def __init__(self, *,
                match: Optional[Match] =None,
                match_list: Optional[List[Match]] =None,
                target: Optional[Target] =None,
                uses_goto: Optional[bool] =False,
                goto_chain: Optional['Chain'] = None):
        """
        :param match: optional :class:`Match` object; if present, it is added
            to the rule's list of :class:`Match` objects
        :param match_list: optional list of :class:`Match` objects;
            if present, it is appended to the rule's list of :class:`Match`
            objects
        :param target: a :class:`Target` object; either this parameter or
            the ``goto_chain`` parameter may be specified
        :param uses_goto:  if ``True``, rule processing continues at the
            specified target (which **must** be a :class:`ChainTarget`)
            short-circuiting any rules following this one in the chain
        :param goto_chain: an optional :class:`Chain` object that is
            the target of this rule via a ``goto`` (instead of ``jump``);
            either this parameter or the ``target`` parameter may be
            specified
        """
        if goto_chain is not None and target is not None:
            raise IptablesError('both target and goto chain specified')
        self.__match_list = []
        if match is not None:
            self.__match_list.append(match)
        if match_list:
            self.__match_list += match_list
        self.__target = target
        self.__uses_goto = uses_goto
        if goto_chain is not None:
            self.__target = ChainTarget(chain=goto_chain)
            self.__uses_goto = True
        self.__packet_count = 0
        self.__byte_count = 0
        self.__owner_chain = None
        self.__rulenum = 0
        # __iptables_line is not None if this rule is created from
        # iptables(8) output
        self.__iptables_line = None
        # The __parsed attribute will be True if the __iptables_line
        # is not None and has been successfully parsed.
        self.__parsed = False
        # Verify that there is at most 1 PacketMatch
        has_packet_match = False
        for mobj in self.__match_list:
            if isinstance(mobj, PacketMatch):
                if has_packet_match:
                    raise IptablesError('more than one PacketMatch in rule')
                has_packet_match = True

    def __str__(self):
        if self.parsing_failed():
            rule_str = f"UNPARSED: {self.__iptables_line}"
        else:
            rule_str = ' '.join(self.to_iptables_args())
        return f"ChainRule('{rule_str}')"

    def __iter__(self):
        """Iterator for the rule's matches
        """
        return iter(self.__match_list)

    def _set_stats(self, *, packet_count: int, byte_count: int):
        """Set the rule stats
        This method is only used by the parsing code.
        """
        self.__packet_count = packet_count
        self.__byte_count = byte_count

    def _set_iptables_line(self, line: str, parsed: bool) -> None:
        """Setting the iptables line marks the rule as unparsed
        """
        self.__iptables_line = line
        self.__parsed = parsed

    def parsing_failed(self) -> bool:
        """Returns ``True`` if the rule has not been parsed successfully
        """
        return (self.__iptables_line is not None and
            (not self.__parsed or isinstance(self.__target, UnparsedTarget)))

    def get_iptables_line(self) -> Optional[str]:
        """Returns the iptables line if this rule was created from
        the output of **iptables(8)**, otherwise it returns ``None``.
        """
        return self.__iptables_line

    def get_packet_count(self) -> int:
        """Returns the packet count of the rule
        """
        return self.__packet_count

    def get_byte_count(self) -> int:
        """Returns the byte count of the rule
        """
        return self.__byte_count

    def get_chain(self) -> 'Chain':
        """Returns the :class:`Chain` where this rule belongs (returns
        ``None`` if this rule is not in any chain)
        """
        return self.__owner_chain

    def get_rulenum(self) -> int:
        """Returns the rule number
        """
        return self.__rulenum

    def _set_chain(self, chain, rulenum: int) -> None:
        """Set the :class:`Chain` where this rule belongs; also sets
        the rule number.
        """
        if self.__owner_chain is not None:
            raise IptablesError("rule belongs to different chain")
        self.__owner_chain = chain
        self.__rulenum = rulenum

    def _inc_rulenum(self) -> None:
        """Increase rulenum by 1; this is used when a rule is inserted
        before this one.
        """
        self.__rulenum += 1

    def _dec_rulenum(self) -> None:
        """Decrease rulenum by 1; this is used when a rule after this
        one is deleted from a chain.
        """
        self.__rulenum -= 1

    def _deleted(self) -> None:
        """Invoked when the rule is deleted
        """
        self.__owner_chain = None
        self.__rulenum = 0

    def get_target(self) -> Optional[Target]:
        """Returns the rule target (a :class:`Target` object) or ``None``
        """
        return self.__target

    def uses_goto(self) -> bool:
        """Returns ``True`` if this rule 'goes' to its (chain) target
        instead of 'jumping' to it.
        """
        return self.__uses_goto

    def _set_target(self, target: Target) -> None:
        """Change the rule's target without checking if the
        rule belongs to a chain.
        """
        self.__target = target
        if (isinstance(self.__target, UnparsedTarget) and
                not isinstance(target, UnparsedTarget) and
                    self.__iptables_line is not None):
            self.__parsed = True

    def set_target(self, target: Target) -> None:
        """Set the rule target
        """
        if self.__owner_chain is not None:
            raise IptablesError('attempt to replace target of active rule')
        self.__target = target

    def iter_match_list(self) -> Iterator[Match]:
        """Returns an iterator for the matches of this rule.

        **This method is deprecated and will be removed at a future version.**
        """
        return iter(self.__match_list)

    def iter_matches(self, lookfor: Optional[Match] =None) -> Iterator[Match]:
        """Returns an iterator for the matches of this rule.
        If ``lookfor`` is not ``None``, the iterator will return
        :class:`Match` instances with criteria that compare equal to those of
        the ``lookfor`` :class:`Match`; if ``lookfor`` has no criteria
        defined, the iterator will return :class:`Match` instances of
        the **same** type as the ``lookfor`` :class:`Match`.
        """
        if lookfor is None:
            return iter(self.__match_list)
        lookfor_klass = type(lookfor)
        for crit in lookfor.get_criteria():
            if crit is not None and crit.is_set():
                # Perform a match value comparison
                lookfor_klass = type(None)
                break
        return filter(lambda m: lookfor_klass is type(m) or m == lookfor,
                        self.__match_list)

    def get_match_count(self) -> int:
        """Returns the number of matches.
        """
        return len(self.__match_list)

    def get_match_list(self) -> List[Match]:
        """Returns the match list of this rule.
        """
        return self.__match_list[:]

    def has_match(self, match: Match, is_only_match=True) -> bool:
        """Returns ``True`` if the match list of this rule consists only
        of the specified match
        (when ``is_only_match`` is ``True``)
        or if the match list contains the specified match
        (when ``is_only_match`` is ``False``).

        An object of :class:`MatchNone` can be
        used to test for an empty match list.
        """
        if isinstance(match, MatchNone):
            return not bool(self.__match_list)
        if is_only_match:
            if len(self.__match_list) != 1:
                return False
            return match == self.__match_list[0]
        for existing_match in self.__match_list:
            if match == existing_match:
                return True
        return False

    def has_target(self, target: Target) -> bool:
        """Returns ``True`` if the rule has the specified target.
        An object of :class:`TargetNone` can be used to test for lack
        of target.
        """
        if isinstance(target, TargetNone):
            return self.__target is None
        return self.__target == target

    def targets_chain(self, chain: 'Chain') -> bool:
        """Returns ``True`` if the target of this rule is the specified chain

        :param chain: a :class:`Chain` object
        """
        # Must invoke the get_target_chain() method to force lazy resolution
        # of the Chain object
        target_chain = self.get_target_chain()
        return (target_chain is not None and
                target_chain.get_real_name() == chain.get_real_name())

    def get_target_chain(self) -> Optional['Chain']:
        """Returns the :class:`Chain` object that is
        the target of this rule, or ``None`` if this rule does not
        target a chain.
        """
        if not isinstance(self.__target, ChainTarget):
            return None
        target_chain = self.__target.get_chain()
        if target_chain is not None:
            return target_chain
        # The ChainTarget may only have the chain name, but not the
        # chain object; try to resolve it
        pft = self.__owner_chain.get_pft()
        if pft is None:
            raise IptablesError("rule is not in IptablesPacketFilterTable")
        return self.__target.resolve_chain(pft)

    def matches_all_packets(self) -> bool:
        """Returns ``True`` iff this rule matches all packets. This
        can be because the rule has no matches, or because the only
        matches are comments.
        """
        for match in self.__match_list:
            if not isinstance(match, CommentMatch):
                return False
        return True

    def to_iptables_args(self) -> List[str]:
        """Returns a list suitable to be used as an argument to
        the **iptables(8)** command

        Raises an :exc:`IptablesError` if this is an unparsed rule
        """
        if self.parsing_failed():
            raise IptablesError(f'unable to parse rule: {self.__iptables_line}')
        retval = []
        for match in self.__match_list:
            retval += match.to_iptables_args()
        if self.__target is not None:
            target_args = self.__target.to_iptables_args()
            if target_args:
                retval.append('-g' if self.__uses_goto else '-j')
                retval += target_args
        return retval

    def jump_to(self, *, target: Optional[Target] =None,
                            chain: Optional['Chain'] =None) -> 'ChainRule':
        """Add a jump to the specified target.
        The target is identified either via the ``target`` argument or
        via the ``chain`` argument.

        Raises an :exc:`IptablesError` if:
            - both ``target`` and ``chain`` arguments are not ``None``
            - the rule is already part of a :class:`Chain`

        :param target: optional :class:`Target` object
        :param chain: optional :class:`Chain` object
        :rtype: this :class:`ChainRule` object
        """
        if self.__owner_chain is not None:
            rcn = self.__owner_chain.get_real_name()
            raise IptablesError(f'rule already inserted in chain {rcn}')
        if target is not None and chain is not None:
            raise IptablesError('both target and chain specified')
        if chain is not None:
            target = ChainTarget(chain=chain)
        self.__target = target
        return self

    def go_to(self, *, chain: 'Chain') -> 'ChainRule':
        """Add a goto to the specified chain.

        Raises an :exc:`IptablesError` if the rule is already part
        of a :class:`Chain`

        :param chain: a :class:`Chain` object
        :rtype: this :class:`ChainRule` object
        """
        if self.__owner_chain is not None:
            rcn = self.__owner_chain.get_real_name()
            raise IptablesError(f'rule already inserted in chain {rcn}')
        self.__target = ChainTarget(chain=chain)
        self.__uses_goto = True
        return self

    def zero_counters(self) -> None:
        """Zero the packet and byte counters of this rule
        """
        if self.__owner_chain is None:
            raise IptablesError('rule not in a chain')
        pft = self.__owner_chain.get_pft()
        if pft is None:
            raise IptablesError('rule belongs to chain that is not in kernel')
        pft.zero_counters(chain=self.__owner_chain, rulenum=self.__rulenum)

    __PROTO_NAMES = set(('tcp', 'udp', 'udplite', 'icmp',
                                'esp', 'ah', 'sctp', 'all'))

    @classmethod
    def __parse_target_name(cls, field_iter: LookaheadIterator):
        """Returns the target_name if present, otherwise None
        """
        #
        # Sample lines:
        # pkts bytes  target  prot  opt  in  out  source      destination
        #    0     0         !22    --   *   *    0.0.0.0/0   0.0.0.0/0
        #    0     0  foo     all   --   *   *    0.0.0.0/0   0.0.0.0/0
        #
        # The field_iter has already returned the pkts and bytes fields.
        #
        candidate = next(field_iter)
        # If all upper-case, assume it is a target
        if candidate.isupper():
            return candidate
        # If it starts with a '!', it is a protocol
        if candidate[0] == '!' or candidate.isdigit():
            field_iter.put_back(candidate)
            return None
        if candidate not in cls.__PROTO_NAMES:
            return candidate
        # At this point we know that the candidate field matches a protocol
        # name, but it is possible that there is a chain named after a
        # protocol. So we test if the next field might be a protocol
        nextone = field_iter.peek()
        if nextone[0] == '!':
            nextone = nextone[1:]
        if nextone.isdigit() or nextone in cls.__PROTO_NAMES:
            return candidate
        field_iter.put_back(candidate)
        return None

    @classmethod
    def create_from_existing(cls,   # pylint: disable=too-many-locals
                        iptables_output_line: str,
                        pft: 'IptablesPacketFilterTable') -> 'ChainRule':
        """Create a ChainRule from a line of ``iptables -xnv`` output

        :param iptables_output_line: line of ``iptables -xnv`` output
        :param pft: an :class:`IptablesPacketFilterTable` object
        """
        fields = iptables_output_line.split()
        # Minimum lookahead is 3, in order to support put_back based
        # on peek'ed value
        field_iter = LookaheadIterator(fields, 3)
        try:
            packet_count = int(next(field_iter))
            byte_count = int(next(field_iter))
            target_name = cls.__parse_target_name(field_iter)
            # pylint: disable=protected-access
            packet_match = PacketMatch._parse(field_iter, ipv6=pft.is_ipv6())
            # pylint: enable=protected-access
            # Check for '[goto]'
            uses_goto = False
            if field_iter.peek() == '[goto]':
                _ = next(field_iter)
                uses_goto = True
            parser = MatchParser(field_iter, ipv6=pft.is_ipv6())
            match_list = parser.parse_matches()
            new_field_iter = RuleFieldIterator(field_iter, 3)
            parser = TargetParser(target_name, new_field_iter,
                                        ipv6=pft.is_ipv6())
            target = parser.parse_target(uses_goto)
            stored_fields = new_field_iter.get_stored_fields()
            if stored_fields:
                raise IptablesParsingError(
                    f"unparsed fields: {' '.join(stored_fields)}")
        except IptablesParsingError as parserr:
            parserr.set_line(iptables_output_line)
            raise
        except StopIteration as stopit:
            raise IptablesParsingError('insufficient number of fields',
                                line=iptables_output_line) from stopit
        except ValueError as valerr:
            raise IptablesParsingError('bad field value',
                                line=iptables_output_line) from valerr
        rule = ChainRule(match=packet_match, match_list=match_list,
                                target=target, uses_goto=uses_goto)
        rule._set_stats(packet_count=packet_count, byte_count=byte_count)
        if isinstance(target, (ChainTarget, UnparsedTarget)):
            # An UnparsedTarget may really be a ChainTarget
            # We currently assume that targets with all-upper-case names
            # are target extensions, but this may not always be the case.
            # So we will try to resolve the target name as a chain name
            # after we have collected all the chain names.
            pft._add_unresolved_rule(rule)   # pylint: disable=protected-access
        rule._set_iptables_line(iptables_output_line, True)
        return rule

    @classmethod
    def _create_unparsed_rule(cls, iptables_line: str) -> 'ChainRule':
        """Create an unparsed rule
        """
        rule = ChainRule()
        rule._set_iptables_line(iptables_line, False)
        return rule
