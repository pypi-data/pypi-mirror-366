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

"""A programmatic interface to the iptables command
"""

import logging
import subprocess
import time

from typing import Iterator, List, Mapping, Optional, Tuple

from .exceptions import (
                IptablesError, IptablesParsingError, IptablesExecutionError)
from .chain import Chain, BuiltinChain
from .targets import Target, ChainTarget, UnparsedTarget
from .deps import get_logger

_logger = get_logger("linuxnet.iptables.table")


def _run(*args, **kwargs) -> subprocess.CompletedProcess:
    """This function consumes the 'execute_always' parameter (it does
    nothing with it).

    Callables used in place of this function need to be aware of
    the execute_always flag.
    """
    kwargs.pop('execute_always', None)
    # pylint: disable=subprocess-run-check
    try:
        return subprocess.run(*args, **kwargs)
    except Exception as ex:         # pylint: disable=broad-except
        raise IptablesExecutionError("iptables execution error") from ex
    # pylint: enable=subprocess-run-check


# pylint: disable=too-many-instance-attributes, too-many-public-methods

class IptablesPacketFilterTable:
    """A netfilter table containing chains.

    The chains accessible via the methods of this class may be pruned
    based on an optionally provided prefix. Furthermore, when new
    chains are created, the prefix may be automatically added to
    the specified chain name.

    A chain name without the prefix is referred to as the **logical**
    chain name, while the full chain name is referred to as the **real**
    chain name. When no prefix is specified, the logical and real names
    are identical.

    Multiple :class:`IptablesPacketFilterTable` objects for the same
    underlying netfilter table are not guaranteed to be in-sync.

    An :class:`IptablesPacketFilterTable` instance if either IPv4-specific
    or IPv6-specific depending on initialization.
    """
    BUILTIN_CHAINS = {
                        'filter' : ('INPUT', 'OUTPUT', 'FORWARD'),
                        'mangle' : ('INPUT', 'FORWARD', 'PREROUTING',
                                        'POSTROUTING', 'OUTPUT'),
                        'nat' : ('PREROUTING', 'POSTROUTING', 'OUTPUT'),
                        'raw' : ('PREROUTING', 'OUTPUT'),
                        'security' : ('INPUT', 'OUTPUT', 'FORWARD'),
                    }

    __CHAIN_NAME_LIMIT = 28

    def __init__(self, table_name: str, chain_prefix: Optional[str] =None,
                        runner=None, *, ipv6=False):
        """
        :param table_name: one of ``filter``, ``mangle``, ``nat``, ``raw``,
            or ``security``
        :param chain_prefix: if specified, user chains are split into two
            groups: those with names starting with the prefix and those
            that don't) with methods like :meth:`get_user_chains`
            returning only these user chains;
            the chain name that excludes the prefix is referred to as
            the **logical** chain name
        :param runner: optional Callable object used to invoke the
            **iptables(8)** command. The object should have the same signature
            as :func:`subprocess.run` and provide the same functionality.
            It also needs to consume the ``execute_always`` boolean parameter;
            this parameter is used to indicate that the **iptables(8)** command
            should be invoked even if the ``runner`` is in dryrun mode (this
            is used for read-only commands like ``iptables -L``).
            The default is to use a function with similar functionality
            as :func:`subprocess.run`.
        :param ipv6: if ``True``, this is an IPv6-specific instance
            (i.e. **ip6tables(8)** will be invoked in place of **iptables(8)**)
        """
        if table_name not in self.BUILTIN_CHAINS:
            raise IptablesError(f"unknown table '{table_name}'")
        self.__prefix = chain_prefix
        self.__table_name = table_name
        self.__runner = runner or _run
        self.__ipv6 = ipv6
        # If chain_prefix is not None, the __chain_map will contain
        # only chains whose name starts with this prefix, otherwise
        # it will contain all chains.
        # The built-in chains are always included.
        # Key: real chain-name
        # Value: Chain
        self.__chain_map = {}
        # If chain_prefix is not None, the __other_chain_map will contain
        # all chains that were not included in __chain_map
        # Key: real chain-name
        # Value: Chain
        self.__other_chain_map = {}
        self.__unresolved_rules = None
        self.__unparsed_chain_count = 0
        self.__unresolved_target_count = 0
        # This is the time we read the iptables configuration
        self.__timestamp = None
        # The epoch is bumped every time we read the iptables configuration
        self.__epoch = 0

    def __str__(self):
        return f'IptablesPacketFilterTable({self.__table_name})'

    def is_handler_of(self, rcn: str) -> bool:
        """Returns ``True`` if the real chain name ``rcn`` matches the
        prefix of this :class:`IptablesPacketFilterTable`,
        or if this :class:`IptablesPacketFilterTable` has no prefix.

        :param rcn: real chain name
        """
        return (self.__prefix is None or
                    rcn in self.BUILTIN_CHAINS.get(self.__table_name, ()) or
                        rcn.startswith(self.__prefix))

    def is_ipv6(self) -> bool:
        """Returns ``True`` if this table is for IPv6
        """
        return self.__ipv6

    def get_table_name(self) -> str:
        """Returns the table name
        """
        return self.__table_name

    def get_prefix(self) -> Optional[str]:
        """Returns the chain prefix
        """
        return self.__prefix

    def set_prefix(self, prefix: Optional[str]) -> None:
        """Partition (or repartition) the user chains according to the
        specified prefix.

        :param prefix: the new prefix
        """
        chain_map = self.__chain_map.copy()
        chain_map.update(self.__other_chain_map)
        self.__chain_map.clear()
        self.__other_chain_map.clear()
        self.__prefix = prefix
        for rcn, chain in chain_map.items():
            if self.is_handler_of(rcn):
                self.__chain_map[rcn] = chain
            else:
                self.__other_chain_map[rcn] = chain

    def get_timestamp(self) -> Optional[float]:
        """Returns the time that the iptables configuration was read
        (as obtained from :func:`time.time`)
        """
        return self.__timestamp

    def get_epoch(self) -> int:
        """Returns the number of times the iptables configuration has
        been initialized with **iptables(8)** output.
        """
        return self.__epoch

    def get_unparsed_chain_count(self) -> int:
        """Returns the number of chains that were not successfully parsed
        from the output of **iptables(8)**
        """
        return self.__unparsed_chain_count

    def get_unresolved_target_count(self) -> int:
        """Returns the number of rules with unresolved targets from
        the output of **iptables(8)**. This may be due to targets being
        chains that we fail to find, or (more likely) special targets
        that we don't know how to parse.
        """
        return self.__unresolved_target_count

    def rcn2lcn(self, rcn: str) -> str:
        """Convert a real chain name to a logical chain name by stripping
        the prefix (if there is one).

        Raises an :exc:`IptablesError` if this
        :class:`IptablesPacketFilterTable` has a prefix and it is unrelated
        to ``rcn``.

        :param rcn: real chain name
        """
        if self.__prefix is None:
            return rcn
        if rcn in self.BUILTIN_CHAINS.get(self.__table_name, ()):
            return rcn
        if rcn.startswith(self.__prefix):
            return rcn[len(self.__prefix):]
        raise IptablesError(f'attempt to convert unrelated chain name {rcn}')

    def get_builtin_chains(self) -> List[Chain]:
        """Returns a list of the builtin chains
        """
        return [c for c in self.__chain_map.values() if c.is_builtin()]

    def get_user_chains(self) -> List[Chain]:
        """Returns a list of all user (i.e. non-builtin) chains
        """
        return [c for c in self.__chain_map.values() if not c.is_builtin()]

    def get_rules_by_target(self, target: Target) -> List[List['ChainRule']]:
        """The return value is a list of lists: the inner list contains
        :class:`ChainRule` objects with the rules of a particular chain that
        are using the specified target, while the outer list corresponds
        to the chains containing these rules.
        """
        retval = []
        for chain in self.__chain_map.values():
            rule_list = [r for r in chain.get_rules()
                                if r.get_target() == target]
            if rule_list:
                retval.append(rule_list)
        return retval

    def __rcn(self, name: str) -> str:
        """Return the real chain name
        """
        return name if self.__prefix is None else self.__prefix + name

    def get_rcn(self, lcn: str) -> str:
        """Returns the real chain name for the given logical chain name

        :param lcn: logical chain name
        """
        return self.__rcn(lcn)

    def get_chain_map(self) -> Mapping[str, Chain]:
        """Returns a dictionary containing all accessible chains;
        the key is the real chain name (if the
        :class:`IptablesPacketFilterTable` uses a prefix, only chains
        with that prefix, and the builtin chains, will be included)
        """
        return self.__chain_map.copy()

    def get_chain_by_lcn(self, chain_name: str) -> Optional[Chain]:
        """Returns the :class:`Chain` object with the specified name
        or ``None`` if there is no such chain

        :param chain_name: logical chain name
        """
        return self.__chain_map.get(self.__rcn(chain_name))

    # This is here for backwards-compatibity
    get_chain = get_chain_by_lcn

    def get_chain_by_rcn(self, real_chain_name: str) -> Optional[Chain]:
        """Returns the :class:`Chain` object with the specified name
        or ``None`` if there is no such chain

        :param real_chain_name: real chain name
        """
        chain = self.__chain_map.get(real_chain_name)
        if chain is not None:
            return chain
        return self.__other_chain_map.get(real_chain_name)

    def get_chain_by_lcn_prefix(self, prefix: str) -> List[Chain]:
        """Returns a list of :class:`Chain` objects whose logical name
        starts with the specified prefix.

        :param prefix: prefix of logical chain name
        """
        rcn_prefix = self.__rcn(prefix)
        return [chain for rcn, chain in self.__chain_map.items()
                        if rcn.startswith(rcn_prefix)]

    def get_builtin_chain(self, chain_name: str) -> BuiltinChain:
        """Returns the :class:`BuiltinChain` object with the specified
        ``chain_name``.

        :param chain_name: name of builtin chain
        """
        try:
            return self.__chain_map[chain_name]
        except IndexError as idxerr:
            raise IptablesError(
                        f'unknown builtin chain: {chain_name}') from idxerr

    def iptables_run(self, *args, **kwargs) -> subprocess.CompletedProcess:
        """Execute an **iptables(8)** command with the specified arguments.
        The table name is added automatically. For example::

            pft.iptables_run(['-N', 'newchain'])

        will execute the command::

            iptables -t mangle -N newchain

        if the ``pft`` is an :class:`IptablesPacketFilterTable` object
        for the ``mangle`` table.

        Raises an :exc:`IptablesExecutionError` in the event of failure.
        """
        #
        # Prefix the command with 'iptables -t {table_name}'
        # We expect the 1st argument to always be a list - we do not
        # support strings.
        #
        if args:
            # The args is the first argument
            subprocess_args = args[0]
        else:
            subprocess_args = kwargs['args']
        prog = 'ip6tables' if self.__ipv6 else 'iptables'
        subprocess_args = [prog, '-t', self.__table_name] + subprocess_args
        if args:
            new_args = tuple([subprocess_args] + list(args[1:]))
        else:
            new_args = args
            kwargs['args'] = subprocess_args
        # pylint: disable=subprocess-run-check
        try:
            return self.__runner(*new_args, **kwargs)
        except IptablesExecutionError as ipex:
            ipex.set_program(prog)
            raise
        except Exception as ex:         # pylint: disable=broad-except
            raise IptablesExecutionError(
                f"{prog} execution error", program=prog) from ex
        # pylint: enable=subprocess-run-check

    def __resolve_rule_targets(self, log_parsing_failures: bool) -> bool:
        """When we are parsing rules, we may run into chain targets before
        we have parsed the relevant chains. Such targets will be classified
        as UnparsedTarget's. We look for such targets here, and
        convert them to :class:`ChainTarget`'s if needed.
        We also resolve chains for :class:`ChainTarget`'s.
        """
        self.__unresolved_target_count = 0
        for rule in self.__unresolved_rules:
            target = rule.get_target()
            if isinstance(target, ChainTarget):
                chain = target.resolve_chain(pft=self,
                                        log_failure=log_parsing_failures)
                if chain is None:
                    self.__unresolved_target_count += 1
            elif isinstance(target, UnparsedTarget):
                target_name = target.get_target_name()
                if target.get_target_options():
                    self.__unresolved_target_count += 1
                    if log_parsing_failures:
                        _logger.warning(
                            "%s: unable to parse target with options: %s",
                                    self.__resolve_rule_targets.__qualname__,
                                    target_name)
                    continue
                chain = self.get_chain_by_rcn(target_name)
                # pylint: disable=protected-access
                if chain is not None:
                    rule._set_target(ChainTarget(chain=chain))
                elif target_name.isupper():
                    # No options, not-a-chain, and all-upper-case-name ==>
                    # assume it is a Target
                    rule._set_target(Target(target_name, terminates=False))
                else:
                    if log_parsing_failures:
                        _logger.warning(
                            "%s: unable to parse target with no options: %s",
                                    self.__resolve_rule_targets.__qualname__,
                                    target_name)
                    self.__unresolved_target_count += 1
                # pylint: enable=protected-access
        self.__unresolved_rules = None
        return self.__unresolved_target_count == 0

    def _add_unresolved_rule(self, rule) -> None:
        """Add the specified rule to the list of unresolved rules (rules
        where the target needs resolution)
        """
        self.__unresolved_rules.append(rule)

    def __aggregate_rule_stats(self, chain_name: str, log_level,
                rule_iter: Iterator['ChainRule'],
                log_stat_failures: bool) -> Tuple[int, int]:
        """Returns the tuple (packets, bytes) with the total
        number of packets and bytes that have traversed the list of rules
        by heuristically aggregating the stas of each rule.

        The result is an approximation since rules may be added (or
        removed) at different times.
        """
        chain_packet_count = 0
        chain_byte_count = 0
        for rule in rule_iter:
            packet_count = rule.get_packet_count()
            byte_count = rule.get_byte_count()
            #
            # A rule that matches everything will account for the
            # rest of the packets.
            # However, this rule may have been added at a later time
            # in which case its stats would be an incorrect approximation.
            # To alleviate this, we compute the aggregate stats of the
            # remaining rules, and pick the largest value.
            #
            if rule.matches_all_packets():
                packet_count_rest, byte_count_rest = \
                        self.__aggregate_rule_stats(chain_name,
                                    logging.INFO, rule_iter, log_stat_failures)
                chain_packet_count += max(packet_count, packet_count_rest)
                chain_byte_count += max(byte_count, byte_count_rest)
                break
            # If the rule has matching criteria (discounting any
            # CommentMatch'es), then whether we use its stats depends
            # on its target:
            #   - if there is no target, we ignore it
            #   - if it is a goto to a user chain, we add up its stats
            #   - if it is a jump to a user chain, we give up because
            #     we don't know if the chain returns
            #   - if it is a known terminating special target,
            #     we add up its stats
            #   - if it is a known non-terminating special target,
            #     we ignore it
            #   - if it is an unknown special target, we give up
            #
            # The known vs. unknown distinction is based on
            # the targets that can be processed by this package
            # (see target.py)
            target = rule.get_target()
            if target is None:
                continue
            if isinstance(target, ChainTarget):
                if rule.uses_goto():
                    chain_packet_count += packet_count
                    chain_byte_count += byte_count
                    continue
                if log_stat_failures:
                    _logger.log(log_level,
                        "Unable to compute stats for builtin chain %s: "
                        "has rule with match criteria and jump target",
                            chain_name)
                return (0, 0)
            # Check if this is a target that terminates packet processing
            target_name = target.get_target_name()
            try:
                if target.is_terminating():
                    chain_packet_count += packet_count
                    chain_byte_count += byte_count
            except IptablesError:
                if log_stat_failures:
                    _logger.log(log_level,
                        "Unable to compute stats for builtin chain %s: "
                        "has rule with match criteria and unknown "
                        "special target: %s",
                            chain_name, target_name)
                return (0, 0)
        return (chain_packet_count, chain_byte_count)

    def __calculate_builtin_chain_stats(self, log_stat_failures: bool):
        """For all user-chains, we calculate their packet/byte counts
        based on the packet/byte counts of the rules that direct traffic
        to those chains.
        For the builtin chains we need to take a different approach since
        iptables does not report the builtin chain stats. So we calculate
        the packet/byte counts from the packet/byte counts of their rules
        with some heuristics (i.e the packet/byte counts are not guaranteed
        to be accurate).
        """
        for builtin_chain in self.get_builtin_chains():
            chain_packet_count, chain_byte_count = \
                self.__aggregate_rule_stats(
                        builtin_chain.get_real_name(),
                        logging.WARNING,
                        iter(builtin_chain.get_rules()),
                        log_stat_failures)
            builtin_chain._set_stats(    # pylint: disable=protected-access
                        chain_packet_count, chain_byte_count)

    def __clear_chain_info(self) -> None:
        """Disassociate from all known chains
        """
        for chain in self.__chain_map.values():
            chain._clear_pft()          # pylint: disable=protected-access
        for chain in self.__other_chain_map.values():
            chain._clear_pft()          # pylint: disable=protected-access

    def init_from_output(self, iptables_output: str,
                        add_builtins=True, log_parsing_failures=True) -> bool:
        """Initialize the attributes of this :class:`IptablesPacketFilterTable`
        from the output of **iptables(8)**

        :param iptables_output: the output of ``iptables -L -xnv`` as
            included in ``subprocess.CompletedProcess.stdout``
        :param add_builtins: if this parameter is ``True`` then for any
            builtin chain that is not in the ``iptables_output`` (or
            if there is an error parsing its contents), an (empty) chain
            will be added to the :class:`IptablesPacketFilterTable`
        :param log_parsing_failures: if this parameter is ``True`` then
            parsing failures will be logged; such failures are typically
            the result of encountering rules with unknown matches/targets
        :rtype: ``True`` if the ``iptables_output`` is successfully parsed
            with **all** expected builtin chains present, ``False`` otherwise
        """
        self.__clear_chain_info()
        self.__unresolved_rules = []
        self.__unparsed_chain_count = 0
        self.__timestamp = time.time()
        self.__epoch += 1
        init_ok = True
        chains_with_unparsed_rules = []
        for line_group in iptables_output.split('\n\n'):
            try:
                chain = Chain.create_from_existing(line_group.split('\n'),
                                                self, log_parsing_failures)
                # It is possible that the parsing failed because
                # the target could not be resolved.
                # We will consider the failure permanent after we
                # try to resolve targets.
                if chain.get_unparsed_rule_count() != 0:
                    chains_with_unparsed_rules.append(chain)
                self.__add_chain(chain)
            except IptablesParsingError:
                init_ok = False
                self.__unparsed_chain_count += 1
                if log_parsing_failures:
                    _logger.exception("%s: parsing error",
                                self.init_from_output.__qualname__)
        if self.__unresolved_rules:
            if not self.__resolve_rule_targets(log_parsing_failures):
                init_ok = False
        for chain in chains_with_unparsed_rules:
            if chain.get_unparsed_rule_count() != 0:
                init_ok = False
                self.__unparsed_chain_count += 1
        for builtin_name in self.BUILTIN_CHAINS[self.__table_name]:
            if builtin_name in self.__chain_map:
                continue
            init_ok = False
            if log_parsing_failures:
                _logger.warning("Builtin chain not in iptables output: %s",
                                        builtin_name)
            if add_builtins:
                builtin_chain = BuiltinChain(builtin_name, 'ACCEPT', 0, 0)
                self.__add_chain(builtin_chain)
        # Update the packet/byte counts
        # This is done after we have resolved all the rules, so that
        # we know the target chain.
        for chain in self.__chain_map.values():
            # pylint: disable=protected-access
            chain._propagate_rule_stats(log_parsing_failures)
            # pylint: enable=protected-access
        self.__calculate_builtin_chain_stats(log_parsing_failures)
        return init_ok

    def read_system_config(self, add_builtins=True,
                                log_parsing_failures=True) -> bool:
        """Read the current iptables configuration and initialize the
        attributes of this :class:`IptablesPacketFilterTable`.

        :param add_builtins: if this parameter is ``True`` then for any
            builtin chain that is not in the output of ``iptables -xnv -L``
            (or if there is a error parsing its contents), an (empty) chain
            will be added to the :class:`IptablesPacketFilterTable`
        :param log_parsing_failures: if this parameter is ``True`` then
            parsing failures will be logged; such failures are typically
            the result of encountering rules with unknown matches/targets
        :rtype: ``True`` if the  current iptables configuration is
            successfully parsed with **all** expected builtin chains present,
            ``False`` otherwise
        """
        cmd = ['-xnv', '-L']
        proc = self.iptables_run(cmd, check=True, universal_newlines=True,
                                stdout=subprocess.PIPE, execute_always=True)
        return self.init_from_output(proc.stdout, add_builtins=add_builtins,
                                log_parsing_failures=log_parsing_failures)

    def validate_chain_name(self, chain_name: str, *,
                description: Optional[str] =None,
                workaround: Optional[str] =None) -> None:
        """Check if the specified logical chain name is valid.
        Currently, only the name length is checked.
        An :exc:`IptablesError` will be raised if the name is
        not valid.

        :param chain_name: logical chain name
        :param description: text to include in the exception message
            (default: 'chain')
        :param workaround: optional text to include in the exception message
        """
        rcn = self.__rcn(chain_name)
        if len(rcn) <= self.__CHAIN_NAME_LIMIT:
            return
        desc = description or "chain"
        message = (f"length of {desc} name {rcn} ({len(rcn)}) exceeds " +
                        f"{self.__CHAIN_NAME_LIMIT}-character limit")
        if workaround is not None:
            message += f'; {workaround}'
        raise IptablesError(message)

    def create_chain(self, chain_name: str, name_is_logical=True) -> Chain:
        """Create a new chain

        :param chain_name: chain name, either logical or real
        :param name_is_logical: indicates if ``chain_name`` is a logical
            chain name or a real chain name
        """
        rcn = self.__rcn(chain_name) if name_is_logical else chain_name
        _ = self.iptables_run(['-N', rcn], check=True)
        chain = Chain(rcn)
        self.__add_chain(chain)
        return chain

    def __add_chain(self, chain: Chain) -> None:
        """Add the chain to the table
        """
        rcn = chain.get_real_name()
        if self.is_handler_of(rcn):
            self.__chain_map[rcn] = chain
        else:
            self.__other_chain_map[rcn] = chain
        chain._set_pft(self)            # pylint: disable=protected-access

    def delete_chain(self, chain: Chain, delete_referring_rules=True) -> None:
        """Delete the specified chain. The chain is flushed first.

        :param chain: the :class:`Chain` to delete
        :param delete_referring_rules: if ``True``, any rules targetting
            this chain will also be deleted
        """
        if chain.get_pft() is not self:
            raise IptablesError(
                        'attempt to delete chain owned by another table')
        real_chain_name = chain.get_real_name()
        if real_chain_name not in self.__chain_map:
            raise IptablesError(f"chain not present: {real_chain_name}")
        if delete_referring_rules:
            n_deleted = 0
            for existing_chain in self.__chain_map.values():
                n_deleted += existing_chain.delete_rule_by_target_chain(chain)
            _logger.info("%s: %s: deleted %d rules referring to chain %s",
                        self.delete_chain.__qualname__,
                                self, n_deleted, real_chain_name)
        chain.flush()
        _ = self.iptables_run(['-X', real_chain_name], check=True)
        self.__chain_map.pop(real_chain_name, None)
        chain._clear_pft()              # pylint: disable=protected-access

    def zero_counters(self, chain: Optional[Chain] =None,
                                rulenum: Optional[int] =None) -> None:
        """Zero the packet and byte counters for the specified chain
        or chain rule in the kernel. If no chain is specified, all chain
        counters are zero'd.

        Note that this method does not affect the counters of :class:`Chain`
        or :class:`ChainRule` objects which will maintain the values they
        had from the last time the system configuration was read.
        """
        cmd = ['-Z']
        if chain is not None:
            if chain.get_pft() is not self:
                raise IptablesError(
                    'attempt to zero chain counters of '
                    'chain owned by another table')
            cmd.append(chain.get_real_name())
            if rulenum is not None:
                cmd.append(str(rulenum))
        _ = self.iptables_run(cmd, check=True)

# pylint: enable=too-many-instance-attributes, too-many-public-methods
