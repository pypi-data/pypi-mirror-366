# Copyright (c) 2022, 2023, 2024, 2025, Panagiotis Tsirigotis

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

"""Unit-test code for linuxnet.iptables
"""

# pylint: disable=line-too-long, too-many-lines, wrong-import-position

import logging
import os
import subprocess
import unittest
import sys

from collections import namedtuple
from ipaddress import IPv4Network, IPv4Address, IPv6Network, IPv6Address

curdir = os.getcwd()
if os.path.basename(curdir) == 'tests':
    sys.path.insert(0, '..')
    TESTDIR = '.'
else:
    sys.path.insert(0, '.')
    TESTDIR = 'tests'

from linuxnet.iptables import (
                IptablesPacketFilterTable,
                IptablesError,
                ChainRule,
                # Targets
                ChainTarget, Targets,
                MarkTarget, ConnmarkTarget,
                RejectTarget,
                MasqueradeTarget,
                NFLogTarget,
                NoTrackTarget,
                SetTarget,
                Target,
                TtlTarget,
                TraceTarget,
                # Matches
                CommentMatch,
                ConnbytesMatch,
                ConnmarkMatch,
                ConntrackMatch,
                IcmpMatch,
                TcpMatch,
                TcpmssMatch,
                LengthMatch,
                LimitMatch,
                MacMatch,
                MultiportMatch,
                OwnerMatch,
                PacketMatch,
                PacketTypeMatch,
                RecentMatch,
                SetMatch,
                StatisticMatch,
                UdpMatch,
                MatchNone,
                )

root_logger = logging.getLogger()
root_logger.addHandler(logging.FileHandler('test.log', 'w'))
root_logger.setLevel(logging.INFO)


ExecutedCommand = namedtuple('ExecutedCommand', ['cmd', 'args', 'kwargs'])


class SimulatedIptablesRun:     # pylint: disable=too-few-public-methods
    """Simulate a run of iptables
    """
    def __init__(self, exitcode, output):
        self.__output = output
        self.__exitcode = exitcode
        # A run is a list of ExecutedCommand instances
        self.__run = []

    def get_run(self):
        """Retuns the run list
        """
        return self.__run

    def clear_run(self):
        """Clear the run list
        """
        self.__run.clear()

    def __call__(self, cmd, *args, **kwargs):
        self.__run.append(ExecutedCommand(cmd, args, kwargs))
        proc = subprocess.CompletedProcess(args, self.__exitcode)
        proc.stdout = self.__output
        return proc


class TestParsing(unittest.TestCase):
    """Test parsing of iptables output.

    This class contains generic tests; match-specific
    or target-specific tests have their own class below.
    """

    EMPTY_FORWARD = """\
Chain FORWARD (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_OUTPUT = """\
Chain OUTPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_PREROUTING = """\
Chain PREROUTING (policy ACCEPT 429581 packets, 46536920 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_POSTROUTING = """\
Chain POSTROUTING (policy ACCEPT 26246841 packets, 13324987010 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_INPUT = """\
Chain INPUT (policy ACCEPT 28770515 packets, 54867569862 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""

    def test_parsing_goto(self):
        """Parse output with goto
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
   51546 10772289 ingress_eth0  all  --  eth0   *       0.0.0.0/0            0.0.0.0/0           [goto]
  541002 34654910 ingress_lo  all  --  lo     *       0.0.0.0/0            0.0.0.0/0           [goto]

Chain ingress_lo (1 references)
    pkts      bytes target     prot opt in     out     source               destination
  541002 34654910 RETURN     all  --  *      *       127.0.0.0/8          0.0.0.0/0
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain ingress_eth0 (1 references)
    pkts      bytes target     prot opt in     out     source               destination
   51517 10762427 RETURN     all  --  *      *       172.30.1.0/24        0.0.0.0/0
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        for rule in input_chain.get_rules():
            self.assertNotEqual(rule.get_target_chain(), None)
            self.assertTrue(rule.uses_goto())

    def test_parsing_refcounts(self):
        """Parse output with chain refcounts
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
196245663 314408786102 bad_traffic  all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain bad_traffic (2 references)
    pkts      bytes target     prot opt in     out     source               destination
       8      524 DROP         tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           tcpmss match 1:500

Chain FORWARD (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
173219064 146017114276 bad_traffic  all  --  *      *       0.0.0.0/0            0.0.0.0/0
""" + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_chain('bad_traffic')
        self.assertEqual(input_chain.get_reference_count(), 2)

    def test_parsing_missing_chain(self):
        """Parse output with missing chain
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
196245663 314408786102 prod_INPUT  all  --  *      *       0.0.0.0/0            0.0.0.0/0
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        init_ok = pft.init_from_output(output, log_parsing_failures=False)
        self.assertFalse(init_ok, 'failed bad output')

    def test_parsing_upper_case_target(self):
        """Parse output with upper-case chain name
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
    1002     4910 ZOOM        all  --  *      *       0.0.0.0/0            0.0.0.0/0
  541002 34654910 INGRESS-LO  all  --  lo     *       0.0.0.0/0            0.0.0.0/0

Chain INGRESS-LO (1 references)
    pkts      bytes target     prot opt in     out     source               destination
  541002 34654910 RETURN     all  --  *      *       127.0.0.0/8          0.0.0.0/0
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 2)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                target = rule.get_target()
                self.assertTrue(isinstance(target, Target))
                self.assertEqual(target.get_target_name(), "ZOOM")
            elif rulenum == 2:
                target = rule.get_target()
                self.assertTrue(isinstance(target, ChainTarget))
                self.assertEqual(target.get_target_name(), "INGRESS-LO")


class TestIPv6(unittest.TestCase):
    """Test parsing of ip6tables output.
    """

    EMPTY_FORWARD = """\
Chain FORWARD (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_OUTPUT = """\
Chain OUTPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_PREROUTING = """\
Chain PREROUTING (policy ACCEPT 429581 packets, 46536920 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_POSTROUTING = """\
Chain POSTROUTING (policy ACCEPT 26246841 packets, 13324987010 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_INPUT = """\
Chain INPUT (policy ACCEPT 28770515 packets, 54867569862 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""

    def test_parsing_ip6tables_output(self):
        """Parse output with chain refcounts
        """
        output = """\
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 ACCEPT     tcp      *      *       aa00::/64            ::/0                 tcp flags:0x17/0x02
       0        0            udp      *      *       ::/0                 aa00:1234::/32
       0        0 DROP       tcp      *      *       aa00::/64            aa00:1234::/32       tcp flags:0x17/0x02
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter', ipv6=True)
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 3)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                target = rule.get_target()
                self.assertTrue(isinstance(target, Target))
                self.assertEqual(target.get_target_name(), "ACCEPT")
                self.assertEqual(rule.get_match_count(), 2)
                match_list = rule.get_match_list()
                match = match_list[0]
                self.assertTrue(isinstance(match, PacketMatch))
                self.assertTrue(match.source_address().is_set() and
                        match.source_address().get_value() == IPv6Network('aa00::/64'))
            elif rulenum == 2:
                target = rule.get_target()
                self.assertTrue(target is None)
                self.assertEqual(rule.get_match_count(), 1)
                match_list = rule.get_match_list()
                match = match_list[0]
                self.assertTrue(isinstance(match, PacketMatch))
                self.assertTrue(match.dest_address().is_set() and
                        match.dest_address().get_value() == IPv6Network('aa00:1234::/32'))
            elif rulenum == 3:
                target = rule.get_target()
                self.assertTrue(isinstance(target, Target))
                self.assertEqual(target.get_target_name(), "DROP")

    def test_parsing_snat_target_ipv6(self):
        """Parse output with SNAT target
        """
        output = (self.EMPTY_PREROUTING + '\n' + """\
Chain POSTROUTING (1 references)
    pkts      bytes target     prot opt in     out     source               destination
  466007 51946882 SNAT       all      *      eth1    ::/0                 ::/0                to:aa00:d2::aa:bb random-fully
""" + '\n' + self.EMPTY_OUTPUT)
        pft = IptablesPacketFilterTable('nat', ipv6=True)
        self.assertTrue(pft.init_from_output(output))
        postrouting_chain = pft.get_builtin_chain('POSTROUTING')
        rule = next(iter(postrouting_chain))
        target = rule.get_target()
        self.assertEqual(target.get_target_name(), 'SNAT')
        self.assertEqual(target.get_address(), IPv6Address('aa00:d2::aa:bb'))
        self.assertTrue(target.is_fully_random())

    def test_chain_creation_deletion(self):
        """Create, then delete a chain.
        """
        runner = SimulatedIptablesRun(0, None)
        pft = IptablesPacketFilterTable('filter', runner=runner, ipv6=True)
        #
        # Chain creation
        #
        chain = pft.create_chain('test_chain')
        commands = runner.get_run()
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].cmd,
                        ['ip6tables', '-t', 'filter', '-N', 'test_chain'])
        runner.clear_run()
        #
        # Chain deletion
        #
        pft.delete_chain(chain)
        commands = runner.get_run()
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0].cmd,
                        ['ip6tables', '-t', 'filter', '-F', 'test_chain'])
        self.assertEqual(commands[1].cmd,
                        ['ip6tables', '-t', 'filter', '-X', 'test_chain'])


class TestMatchParsing(unittest.TestCase):
    """Test parsing of matches in iptables output
    """

    EMPTY_FORWARD = """\
Chain FORWARD (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_OUTPUT = """\
Chain OUTPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_PREROUTING = """\
Chain PREROUTING (policy ACCEPT 429581 packets, 46536920 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_POSTROUTING = """\
Chain POSTROUTING (policy ACCEPT 26246841 packets, 13324987010 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_INPUT = """\
Chain INPUT (policy ACCEPT 28770515 packets, 54867569862 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""

    def test_parsing_packet_match(self):
        """Parse output with packet match (protocol, fragment,
        source addr, dest addr).
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 DROP         all  -f  *      *       127.0.0.0/8          0.0.0.0/0
       0        0 DROP         2    --  *      *       0.0.0.0/0            0.0.0.0/0
      29     9862 ACCEPT       udp  --  *      *       0.0.0.0/0              10.10.0.0/16
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 3)
        for rule in input_chain:
            if rule.get_rulenum() == 1:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                self.assertTrue(match.fragment().is_positive())
                src = match.source_address()
                self.assertTrue(src.is_positive() and
                    src.get_value() == IPv4Network('127.0.0.0/8'))
            elif rule.get_rulenum() == 2:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                prot = match.protocol()
                self.assertTrue(prot.is_positive() and
                    prot.get_value() == 'igmp')
            elif rule.get_rulenum() == 3:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                prot = match.protocol()
                self.assertTrue(prot.is_positive() and
                    prot.get_value() == 'udp')
                dest = match.dest_address()
                self.assertTrue(dest.is_positive() and
                    dest.get_value() == IPv4Network('10.10.0.0/16'))
        #
        # Test protocol comparison by number, number-in-string-form,
        # and protocol name, where the protocol name is reported by iptables
        # as a number. We use IGMP (protocol number 2) for this.
        #
        rule = next(input_chain.iter_rules(match=PacketMatch().protocol().equals(2)), None)
        self.assertTrue(rule is not None and
                        next(iter(rule)).protocol().get_value() == 'igmp')
        rule = next(input_chain.iter_rules(match=PacketMatch().protocol().equals("2")), None)
        self.assertTrue(rule is not None and
                        next(iter(rule)).protocol().get_value() == 'igmp')

    def test_parsing_packet_type_match(self):
        """Parse output with packet type match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
      29     9862 DROP       all  --  *      *       0.0.0.0              0.0.0.0/0           PKTTYPE = broadcast
      29     9862 ACCEPT     udp  --  *      *       0.0.0.0/0            10.10.0.0/16
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        first_rule = next(iter(input_chain))
        match_list = first_rule.get_match_list()
        self.assertEqual(len(match_list), 2)
        match = match_list[1]
        self.assertTrue(isinstance(match, PacketTypeMatch))
        ptype = match.packet_type()
        self.assertTrue(ptype.is_positive() and
                        ptype.get_value() == 'broadcast')

    def test_parsing_tcp_match(self):
        """Parse output with match related to TCP (port, flags, MSS)
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       8      524 DROP  tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           tcpmss match 1:500
    2182   251300 DROP  tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           tcp flags:!0x17/0x02 option=10
      17      732 ACCEPT  tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           tcp dpt:22 option=!10
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 3)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            match_list = rule.get_match_list()
            # There is a PacketMatch matching the packet protocol
            self.assertEqual(len(match_list), 2)
            match = match_list[-1]
            if rulenum == 1:
                self.assertTrue(isinstance(match, TcpmssMatch))
                mss = match.mss()
                self.assertTrue(mss.is_positive() and
                                        mss.get_value() == (1, 500))
            elif rulenum == 2:
                self.assertTrue(isinstance(match, TcpMatch))
                flags = match.tcp_flags()
                self.assertTrue(flags.is_syn_only() and
                                        not flags.is_positive())
                tcp_option = match.tcp_option()
                self.assertTrue(tcp_option.get_value() == 10 and
                                tcp_option.is_positive())
            elif rulenum == 3:
                self.assertTrue(isinstance(match, TcpMatch))
                dport = match.dest_port()
                self.assertTrue(dport.is_positive() and
                        dport.get_value()[0] == 22)
                tcp_option = match.tcp_option()
                self.assertTrue(tcp_option.get_value() == 10 and
                                not tcp_option.is_positive())

    def test_parsing_udp_match(self):
        """Parse output with match related to UDP
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
      17      732 ACCEPT  udp  --  *      *       0.0.0.0/0            0.0.0.0/0           udp dpt:53
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 1)
        first_rule = next(iter(input_chain))
        match_list = first_rule.get_match_list()
        # There is a PacketMatch matching prot
        self.assertEqual(len(match_list), 2)
        match = match_list[-1]
        self.assertTrue(isinstance(match, UdpMatch))
        dport = match.dest_port()
        self.assertTrue(dport.is_positive() and
                        dport.get_value()[0] == 53)

    def test_parsing_icmp_match(self):
        """Parse output with match related to ICMP
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
  143588 11622518 DROP         icmp --  *      *       0.0.0.0/0            0.0.0.0/0           icmp type 8
  143588 11622518 DROP         icmp --  *      *       0.0.0.0/0            0.0.0.0/0           icmp !any
  143588 11622518 DROP         icmp --  *      *       0.0.0.0/0            0.0.0.0/0           icmp type 3 icmp !type 3 code 1
  143588 11622518 DROP         icmp --  *      *       0.0.0.0/0            0.0.0.0/0           icmptype 3
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 4)
        for rule in input_chain:
            if rule.get_rulenum() == 1:
                match_list = rule.get_match_list()
                # There is a PacketMatch matching prot
                self.assertEqual(len(match_list), 2)
                match = match_list[-1]
                self.assertTrue(isinstance(match, IcmpMatch))
                icmp_type = match.icmp_type()
                self.assertTrue(icmp_type.is_positive() and
                    icmp_type.get_type_name() == 'echo-request' and
                    icmp_type.get_type_value() == 8)
            elif rule.get_rulenum() == 2:
                match_list = rule.get_match_list()
                self.assertEqual(len(match_list), 2)
                match = match_list[-1]
                self.assertTrue(isinstance(match, IcmpMatch))
                icmp_type = match.icmp_type()
                self.assertTrue(not icmp_type.is_positive() and
                                icmp_type.get_type_name() == 'any')
            elif rule.get_rulenum() == 3:
                match_list = rule.get_match_list()
                self.assertEqual(len(match_list), 3)
                match = match_list[-2]
                self.assertTrue(isinstance(match, IcmpMatch))
                icmp_type = match.icmp_type()
                self.assertTrue(icmp_type.is_positive() and
                                icmp_type.get_type_value() == 3)
                match = match_list[-1]
                self.assertTrue(isinstance(match, IcmpMatch))
                icmp_type = match.icmp_type()
                self.assertTrue(not icmp_type.is_positive() and
                                icmp_type.get_type_value() == 3 and
                                icmp_type.get_code() == 1)
            elif rule.get_rulenum() == 4:
                match_list = rule.get_match_list()
                self.assertEqual(len(match_list), 2)
                match = match_list[-1]
                self.assertTrue(isinstance(match, IcmpMatch))
                icmp_type = match.icmp_type()
                self.assertTrue(icmp_type.is_positive() and
                                icmp_type.get_type_value() == 3)

    def test_parsing_recent_match(self):
        """Parse output that uses recent match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 LOG        all  --  *      *       0.0.0.0/0            0.0.0.0/0           recent: CHECK TTL-Match name: foobar side: source LOG flags 0 level 4
       0        0 LOG        all  --  *      *       0.0.0.0/0            0.0.0.0/0           !recent: SET name: foobar side: source LOG flags 0 level 4
       0        0 MARK       all  --  *      *       0.0.0.0/0            0.0.0.0/0           recent: REMOVE name: foobar side: destMARK set 0xa
       0        0            all  --  *      *       0.0.0.0/0            0.0.0.0/0           !recent: UPDATE seconds: 4 hit_count: 3 name: foobar side: source
       0        0 LOG        all  --  *      *       0.0.0.0/0            0.0.0.0/0           recent: REMOVE name: foobar side: dest/* silly */ LOG flags 0 level 4
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           recent: SET name: OUTPUT side: source mask: 255.255.255.255
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 6)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, RecentMatch))
                action = match.action()
                self.assertTrue(action.is_positive() and
                    action.get_value() == RecentMatch.CHECK)
                self.assertTrue(match.same_ttl().is_positive())
                self.assertTrue(match.name().get_value() == 'foobar')
                self.assertTrue(
                        match.address_selection().get_value() ==
                                        RecentMatch.SOURCE_ADDRESS)
            elif rulenum == 2:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, RecentMatch))
                action = match.action()
                self.assertTrue(not action.is_positive() and
                    action.get_value() == RecentMatch.SET)
                self.assertTrue(match.name().get_value() == 'foobar')
                self.assertTrue(
                        match.address_selection().get_value() ==
                                        RecentMatch.SOURCE_ADDRESS)
            elif rulenum == 3:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, RecentMatch))
                action = match.action()
                self.assertTrue(action.is_positive() and
                    action.get_value() == RecentMatch.REMOVE)
                self.assertTrue(match.name().get_value() == 'foobar')
                self.assertTrue(
                        match.address_selection().get_value() ==
                                        RecentMatch.DEST_ADDRESS)
                self.assertTrue(
                    rule.get_target().get_target_name() == 'MARK')
            elif rulenum == 4:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, RecentMatch))
                action = match.action()
                self.assertTrue(not action.is_positive() and
                    action.get_value() == RecentMatch.UPDATE)
                self.assertTrue(match.name().get_value() == 'foobar')
                self.assertTrue(match.seconds().get_value() == 4)
                self.assertTrue(match.hitcount().get_value() == 3)
                self.assertTrue(
                        match.address_selection().get_value() ==
                                        RecentMatch.SOURCE_ADDRESS)
            elif rulenum == 5:
                self.assertEqual(rule.get_match_count(), 2)
                match_list = rule.get_match_list()
                match = match_list[0]
                self.assertTrue(isinstance(match, RecentMatch))
                action = match.action()
                self.assertTrue(action.is_positive() and
                    action.get_value() == RecentMatch.REMOVE)
                self.assertTrue(match.name().get_value() == 'foobar')
                self.assertTrue(isinstance(match_list[1], CommentMatch))
            elif rulenum == 6:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, RecentMatch))
                self.assertEqual(match.mask().get_value(),
                                        IPv4Address('255.255.255.255'))

    def test_parsing_ipset_match(self):
        """Parse output that uses the (ip)set match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            match-set foo6 src,src,dst,dst
       0        0            all  --  *      *       0.0.0.0/0            0.0.0.0/0            match-set foo6 dst,src return-nomatch packets-eq 10 ! bytes-eq 512
       0        0            all  --  *      *       0.0.0.0/0            0.0.0.0/0            match-set foo6 dst,src ! update-counters ! update-subcounters
       0        0            all  --  *      *       0.0.0.0/0            0.0.0.0/0            ! match-set foo6 dst,src ! update-counters update-subcounters
       0        0            all  --  *      *       0.0.0.0/0            0.0.0.0/0            match-set foo6 dst,src return-nomatch packets-lt 10 bytes-gt 512
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 5)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, SetMatch))
                match_set = match.match_set()
                self.assertTrue(match_set.is_positive() and
                    match_set.get_value() == ('foo6', 'src,src,dst,dst'))
            elif rulenum == 2:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, SetMatch))
                match_set = match.match_set()
                self.assertTrue(match_set.is_positive() and
                    match_set.get_value() == ('foo6', 'dst,src'))
                self.assertTrue(match.return_nomatch().is_set())
            elif rulenum == 3:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, SetMatch))
                match_set = match.match_set()
                self.assertTrue(match_set.is_positive() and
                    match_set.get_value() == ('foo6', 'dst,src'))
                self.assertFalse(match.update_counters().get_value())
                self.assertFalse(match.update_subcounters().get_value())
            elif rulenum == 4:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, SetMatch))
                match_set = match.match_set()
                self.assertTrue(not match_set.is_positive() and
                    match_set.get_value() == ('foo6', 'dst,src'))
                self.assertFalse(match.update_counters().get_value())
                self.assertTrue(match.update_subcounters().get_value())
            elif rulenum == 5:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, SetMatch))
                match_set = match.match_set()
                self.assertTrue(match_set.is_positive() and
                    match_set.get_value() == ('foo6', 'dst,src'))
                self.assertTrue(match.return_nomatch().is_set())
                self.assertTrue(
                        match.packet_counter().get_value() == (10, '<'))
                self.assertTrue(
                        match.byte_counter().get_value() == (512, '>'))

    def test_parsing_statistic_match(self):
        """Parse output that uses the statistic match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0            all  --  *      *       0.0.0.0/0            0.0.0.0/0            statistic mode random probability 0.50000000000
       0        0            all  --  *      *       0.0.0.0/0            0.0.0.0/0            statistic mode random ! probability 0.10000000009
       0        0            all  --  *      *       0.0.0.0/0            0.0.0.0/0            statistic mode nth every 100 packet 10
       0        0            all  --  *      *       0.0.0.0/0            0.0.0.0/0            statistic mode nth ! every 100 packet 10
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 4)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, StatisticMatch))
                mode = match.mode()
                self.assertTrue(mode.get_value() == 'random')
                probability = match.probability()
                self.assertTrue(probability.is_positive() and
                        abs(probability.get_value() - 0.5)*1000 < 1.0)
            elif rulenum == 2:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, StatisticMatch))
                mode = match.mode()
                self.assertTrue(mode.get_value() == 'random')
                probability = match.probability()
                self.assertTrue(not probability.is_positive() and
                        abs((probability.get_value() - 0.1)*1000 < 1.0))
            elif rulenum == 3:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, StatisticMatch))
                mode = match.mode()
                self.assertTrue(mode.get_value() == 'nth')
                every = match.every()
                self.assertTrue(every.is_positive() and
                                        every.get_value() == 100)
                self.assertTrue(match.packet().get_value() == 10)
            elif rulenum == 4:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, StatisticMatch))
                mode = match.mode()
                self.assertTrue(mode.get_value() == 'nth')
                every = match.every()
                self.assertTrue(not every.is_positive() and
                                        every.get_value() == 100)
                self.assertTrue(match.packet().get_value() == 10)

    def test_parsing_owner_match(self):
        """Parse output with match related to UID/GID
        """
        output = self.EMPTY_INPUT + '\n' + self.EMPTY_FORWARD + '\n' + \
"""\
Chain OUTPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       8      524   DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           owner UID match 100
       8      524   DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           ! owner GID match 100
       8      524   DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           owner UID match 100-300 ! owner UID match 200
       8      524   DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           owner socket exists
       8      524   DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           owner GID match 100 ! owner socket exists
       0        0   DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           owner GID match 4000 incl. suppl. groups
"""
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        output_chain = pft.get_builtin_chain('OUTPUT')
        self.assertEqual(output_chain.get_rule_count(), 6)
        for rule in output_chain:
            if rule.get_rulenum() == 1:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                self.assertTrue(isinstance(match, OwnerMatch))
                uid = match.uid()
                self.assertTrue(uid.is_positive() and uid.get_value() == (100, None))
            elif rule.get_rulenum() == 2:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                self.assertTrue(isinstance(match, OwnerMatch))
                gid = match.gid()
                self.assertTrue(not gid.is_positive() and gid.get_value() == (100, None))
            elif rule.get_rulenum() == 3:
                match_list = rule.get_match_list()
                self.assertEqual(len(match_list), 2)
                match = match_list[-2]
                self.assertTrue(isinstance(match, OwnerMatch))
                uid = match.uid()
                self.assertTrue(uid.is_positive() and uid.get_value() == (100, 300))
                match = match_list[-1]
                self.assertTrue(isinstance(match, OwnerMatch))
                uid = match.uid()
                self.assertTrue(not uid.is_positive() and uid.get_value() == (200, None))
            elif rule.get_rulenum() == 4:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                self.assertTrue(isinstance(match, OwnerMatch))
                socket_exists = match.socket_exists()
                self.assertTrue(socket_exists.is_positive())
            elif rule.get_rulenum() == 5:
                #
                # Note that a single match is expected because the owner
                # match criteria are different.
                #
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                self.assertTrue(isinstance(match, OwnerMatch))
                gid = match.gid()
                socket_exists = match.socket_exists()
                self.assertTrue(
                        gid.is_positive() and gid.get_value() == (100, None) and
                        not socket_exists.is_positive())
            elif rule.get_rulenum() == 6:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                self.assertTrue(isinstance(match, OwnerMatch))
                suppl_groups = match.suppl_groups()
                gid = match.gid()
                self.assertTrue(
                        gid.is_positive() and gid.get_value() == (4000, None) and
                        suppl_groups.is_positive())

    def test_parsing_connmark_match(self):
        """Parse output with connmark match
        """
        output = ("""\
Chain PREROUTING (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
  558864 28503489 CONNMARK   all  --  *      *       0.0.0.0/0            0.0.0.0/0           connmark match 0x0 CONNMARK set 0x11
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT + '\n' +
                self.EMPTY_INPUT + '\n' + self.EMPTY_POSTROUTING)
        pft = IptablesPacketFilterTable('mangle')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('PREROUTING')
        self.assertEqual(input_chain.get_rule_count(), 1)
        rule = next(iter(input_chain))
        self.assertEqual(rule.get_match_count(), 1)
        match = next(iter(rule))
        self.assertTrue(isinstance(match, ConnmarkMatch))
        cmark = match.mark()
        self.assertTrue(cmark.is_positive() and cmark.get_value() == (0, None))

    def test_parsing_conntrack_match(self):
        """Parse output with conntrack match
        """
        output = ("""\
Chain PREROUTING (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           ctdir ORIGINAL
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           ctreplsrc 100.100.0.0 ctrepldst 200.200.200.0 ctrepldstport 443 ctdir REPLY
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           ctproto 17 ! ctreplsrc 100.100.0.0 ctreplsrcport 443
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           ctstate NEW ctproto 17 ctreplsrc 100.100.0.0 ! ctstate NEW ctproto 6
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           ctstate NEW ctorigsrc 10.10.0.0/16 ctorigdst 20.20.2.0 ! ctorigsrcport 443 ctexpire 60:300
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT + '\n' +
                self.EMPTY_INPUT + '\n' + self.EMPTY_POSTROUTING)
        pft = IptablesPacketFilterTable('mangle')
        self.assertTrue(pft.init_from_output(output))
        chain = pft.get_builtin_chain('PREROUTING')
        self.assertEqual(len(chain), 5)
        for rule in chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, ConntrackMatch))
                self.assertEqual(match.ctdir().get_value(), 'ORIGINAL')
            elif rulenum == 2:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, ConntrackMatch))
                self.assertEqual(match.ctreplsrc().get_value(), IPv4Network('100.100.0.0/16'))
                self.assertEqual(match.ctrepldst().get_value(), IPv4Network('200.200.200.0/24'))
                self.assertEqual(match.ctrepldstport().get_value()[0], 443)
                self.assertEqual(match.ctdir().get_value(), 'REPLY')
            elif rulenum == 3:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, ConntrackMatch))
                self.assertEqual(match.ctproto().get_value(), 'udp')
                self.assertTrue(not match.ctreplsrc().is_positive() and
                        match.ctreplsrc().get_value() == IPv4Network('100.100.0.0/16'))
                self.assertEqual(match.ctreplsrcport().get_value()[0], 443)
            elif rulenum == 4:
                match_iter = iter(rule)
                match = next(match_iter)
                self.assertTrue(isinstance(match, ConntrackMatch))
                self.assertEqual(match.ctstate().get_value(), 'NEW')
                self.assertEqual(match.ctproto().get_value(), 'udp')
                self.assertEqual(match.ctreplsrc().get_value(), IPv4Network('100.100.0.0/16'))
                match = next(match_iter)
                self.assertTrue(isinstance(match, ConntrackMatch))
                self.assertTrue(not match.ctstate().is_positive() and
                                        match.ctstate().get_value() == 'NEW')
                self.assertEqual(match.ctproto().get_value(), 'tcp')
            elif rulenum == 5:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, ConntrackMatch))
                self.assertEqual(match.ctstate().get_value(), 'NEW')
                self.assertEqual(match.ctorigsrc().get_value(), IPv4Network('10.10.0.0/16'))
                self.assertEqual(match.ctorigdst().get_value(), IPv4Network('20.20.2.0/24'))
                self.assertTrue(not match.ctorigsrcport().is_positive() and
                                        match.ctorigsrcport().get_value()[0] == 443)
                self.assertEqual(match.ctexpire().get_value(), (60, 300))

    def test_parsing_limit_match(self):
        """Parse output with limit match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
  487148 21609270 LOG        all  --  *      *       0.0.0.0/0            0.0.0.0/0           limit: avg 15/min burst 5 LOG flags 0 level 6 prefix `DROP-INPUT: '
  520139 23069461 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        rule = next(iter(input_chain))
        self.assertEqual(rule.get_match_count(), 1)
        match = next(iter(rule))
        limit = match.limit()
        self.assertTrue(limit.is_positive() and
                limit.get_value() == LimitMatch.Rate(15, LimitMatch.Rate.PER_MIN))
        burst = match.burst()
        self.assertTrue(burst.is_positive() and
                burst.get_value() == 5)

    def test_parsing_comment_match(self):
        """Parse output with comment matches
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           /* my comment */
       0        0 REJECT     all  --  *      *       0.0.0.0/0            0.0.0.0/0           /* another comment */ state NEW reject-with icmp-port-unreachable
       0        0 REJECT     all  --  *      *       0.0.0.0/0            0.0.0.0/0           /* another comment */ state NEW /* foo bar */ reject-with icmp-port-unreachable
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                for match in rule:
                    if isinstance(match, CommentMatch):
                        comment = match.comment().get_value()
                        self.assertEqual(comment, 'my comment')
                        break
            elif rulenum == 2:
                for match in rule:
                    if isinstance(match, CommentMatch):
                        comment = match.comment().get_value()
                        self.assertEqual(comment, 'another comment')
                        break
            elif rulenum == 3:
                cit = iter(['another comment', 'foo bar'])
                for match in rule:
                    if isinstance(match, CommentMatch):
                        comment = match.comment().get_value()
                        self.assertEqual(comment, next(cit))

    def test_parsing_addrtype_match(self):
        """Parse output with ADDRTYPE match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           ADDRTYPE match src-type UNICAST dst-type !UNICAST
       0        0 LOG        all  --  *      *       0.0.0.0/0            0.0.0.0/0           ADDRTYPE match src-type !BLACKHOLE dst-type !UNICAST limit-in LOG flags 0 level 4 prefix `ADDR '
       0        0 LOG        all  --  *      *       0.0.0.0/0            0.0.0.0/0           ADDRTYPE match src-type MULTICAST limit-out LOG flags 0 level 4 prefix `MCAST '
       0        0 LOG        all  --  *      *       0.0.0.0/0            0.0.0.0/0           ADDRTYPE match src-type PROHIBIT /* PROHIBIT */ LOG flags 0 level 4 prefix `PROH '
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                src_addr_type = match.src_addr_type()
                self.assertTrue(src_addr_type.is_positive() and
                                src_addr_type.get_value() == 'UNICAST')
                dst_addr_type = match.dst_addr_type()
                self.assertTrue(not dst_addr_type.is_positive() and
                                dst_addr_type.get_value() == 'UNICAST')
            elif rulenum == 2:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                src_addr_type = match.src_addr_type()
                self.assertTrue(not src_addr_type.is_positive() and
                                src_addr_type.get_value() == 'BLACKHOLE')
                dst_addr_type = match.dst_addr_type()
                self.assertTrue(not dst_addr_type.is_positive() and
                                dst_addr_type.get_value() == 'UNICAST')
                self.assertTrue(match.limit_iface_in().is_positive())
            elif rulenum == 3:
                self.assertEqual(rule.get_match_count(), 1)
                match = next(iter(rule))
                src_addr_type = match.src_addr_type()
                self.assertTrue(src_addr_type.is_positive() and
                                src_addr_type.get_value() == 'MULTICAST')
                self.assertTrue(match.limit_iface_out().is_positive())
            elif rulenum == 4:
                match_list = rule.get_match_list()
                self.assertEqual(len(match_list), 2)
                match = match_list[0]
                src_addr_type = match.src_addr_type()
                self.assertTrue(src_addr_type.is_positive() and
                                src_addr_type.get_value() == 'PROHIBIT')

    def test_parsing_mac_match(self):
        """Parse output that uses the mac match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           MAC 11:22:33:44:55:66
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           MAC ! AA:22:33:44:55:66
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 2)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, MacMatch))
                mac_source = match.mac_source()
                self.assertTrue(mac_source.is_positive() and
                    mac_source.get_value() == '11:22:33:44:55:66')
            elif rulenum == 2:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, MacMatch))
                mac_source = match.mac_source()
                self.assertTrue(not mac_source.is_positive() and
                    mac_source.get_value() == 'AA:22:33:44:55:66')

    def test_parsing_multiport_match(self):
        """Parse output that uses the multiport match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           multiport ports 10,20,30:40
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           multiport sports !100:300
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           multiport dports ! 81,82,83,84,85
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 3)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, MultiportMatch))
                ports = match.ports()
                self.assertTrue(ports.is_positive() and
                    ports.get_value() == (10, 20, (30, 40)))
            elif rulenum == 2:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, MultiportMatch))
                ports = match.source_ports()
                self.assertTrue(not ports.is_positive() and
                    ports.get_value() == ((100,300),))
            elif rulenum == 3:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, MultiportMatch))
                ports = match.dest_ports()
                self.assertTrue(not ports.is_positive() and
                    ports.get_value() == (81, 82, 83, 84, 85))

    def test_parsing_connbytes_match(self):
        """Parse output that uses the connbytes match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            connbytes 1000 connbytes mode bytes connbytes direction original
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            connbytes 1000:3000 connbytes mode packets connbytes direction reply
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            connbytes 10:10000 connbytes mode avgpkt connbytes direction both
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            ! connbytes 20:400 connbytes mode avgpkt connbytes direction both
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 4)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, ConnbytesMatch))
                count = match.count()
                self.assertTrue(count.is_positive() and
                                        count.get_value()[0] == 1000)
                self.assertTrue(match.mode().get_value() == 'bytes')
                self.assertTrue(match.direction().get_value() == 'original')
            elif rulenum == 2:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, ConnbytesMatch))
                count = match.count()
                self.assertTrue(count.is_positive() and
                                count.get_value()[0] == 1000 and
                                count.get_value()[1] == 3000)
                self.assertTrue(match.mode().get_value() == 'packets')
                self.assertTrue(match.direction().get_value() == 'reply')
            elif rulenum == 3:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, ConnbytesMatch))
                count = match.count()
                self.assertTrue(count.is_positive() and
                                count.get_value()[0] == 10 and
                                count.get_value()[1] == 10000)
                self.assertTrue(match.mode().get_value() == 'avgpkt')
                self.assertTrue(match.direction().get_value() == 'both')
            elif rulenum == 4:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, ConnbytesMatch))
                count = match.count()
                self.assertTrue(not count.is_positive() and
                                count.get_value()[0] == 20 and
                                count.get_value()[1] == 400)
                self.assertTrue(match.mode().get_value() == 'avgpkt')
                self.assertTrue(match.direction().get_value() == 'both')

    def test_parsing_length_match(self):
        """Parse output that uses the length match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            length 10
       0        0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0            length !20
       0        0 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0            length 30:100
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        self.assertEqual(input_chain.get_rule_count(), 3)
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, LengthMatch))
                length = match.length()
                self.assertTrue(length.is_positive() and
                                        length.get_value()[0] == 10)
            elif rulenum == 2:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, LengthMatch))
                length = match.length()
                self.assertTrue(not length.is_positive() and
                                        length.get_value()[0] == 20)
            elif rulenum == 3:
                match = next(iter(rule))
                self.assertTrue(isinstance(match, LengthMatch))
                length = match.length()
                self.assertTrue(length.is_positive() and
                                length.get_value()[0] == 30 and
                                length.get_value()[1] == 100)

    def test_parsing_unknown_match(self):
        """Parse output with unknown match
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
196245663 314408786102 prod_INPUT  all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain prod_INPUT (1 references)
    pkts      bytes target     prot opt in     out     source               destination
    0     0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0           DSCP match 0x10
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        init_ok = pft.init_from_output(output, log_parsing_failures=False)
        self.assertFalse(init_ok, 'failed bad output')



class TestTargetParsing(unittest.TestCase):
    """Test parsing of targets in iptables output
    """

    EMPTY_FORWARD = """\
Chain FORWARD (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_OUTPUT = """\
Chain OUTPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_PREROUTING = """\
Chain PREROUTING (policy ACCEPT 429581 packets, 46536920 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_POSTROUTING = """\
Chain POSTROUTING (policy ACCEPT 26246841 packets, 13324987010 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
    EMPTY_INPUT = """\
Chain INPUT (policy ACCEPT 28770515 packets, 54867569862 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""

    def test_parsing_set_target(self):
        """Parse output with SET target
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
      10       80 SET        tcp  --  *      *       0.0.0.0/0            1.2.3.4              add-set testchain_set src,dst exist timeout 100
      20       90 SET        tcp  --  *      *       0.0.0.0/0            1.2.3.4              del-set testchain_set src,dst
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                target = rule.get_target()
                self.assertTrue(isinstance(target, SetTarget))
                self.assertEqual(target.get_operation(), SetTarget.ADD_SET)
                self.assertEqual(target.get_ipset_name(), "testchain_set")
                self.assertEqual(target.get_ipset_flags(), ['src', 'dst'])
                self.assertTrue(target.is_updating_existing())
                self.assertEqual(target.get_timeout(), 100)
            elif rulenum == 2:
                target = rule.get_target()
                self.assertTrue(isinstance(target, SetTarget))
                self.assertEqual(target.get_operation(), SetTarget.DEL_SET)
                self.assertEqual(target.get_ipset_name(), "testchain_set")
                self.assertEqual(target.get_ipset_flags(), ['src', 'dst'])

    def test_parsing_log_target(self):
        """Parse output with LOG target
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
  487148 21609270 LOG        all  --  *      *       0.0.0.0/0            0.0.0.0/0           limit: avg 15/min burst 5 LOG flags 12 level 6 prefix `DROP-INPUT: '
  520139 23069461 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        rule = next(iter(input_chain))
        target = rule.get_target()
        self.assertEqual(target.get_log_prefix(), 'DROP-INPUT: ')
        self.assertEqual(target.get_log_level(), '6')
        self.assertTrue(target.is_logging_uid())
        self.assertTrue(target.is_logging_ip_options())
        self.assertFalse(target.is_logging_tcp_options())
        self.assertFalse(target.is_logging_tcp_sequence())

    def test_parsing_nflog_target(self):
        """Parse output with NFLOG target
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 NFLOG      tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp flags:0x11/0x01 nflog-group 101 nflog-threshold 10
       0        0 NFLOG      all  --  *      *       0.0.0.0/0            0.0.0.0/0            owner UID match 100 nflog-prefix "hello there "
       0        0 NFLOG      all  --  *      *       0.0.0.0/0            0.0.0.0/0            ctstate INVALID nflog-prefix "invalid state \\\"xyz\\\"" nflog-group 101 nflog-size 42 nflog-threshold 10
       0        0 NFLOG      udp  --  *      *       0.0.0.0/0            0.0.0.0/0            udp dpt:53 nflog-prefix nflog-group nflog-group 100 nflog-size 42
       0        0 NFLOG      udp  --  *      *       0.0.0.0/0            0.0.0.0/0            udp dpt:53 nflog-prefix "tricky nflog-prefix \\\" " nflog-group 100 nflog-size 42
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                target = rule.get_target()
                self.assertTrue(isinstance(target, NFLogTarget))
                self.assertEqual(target.get_nflog_group(), 101)
                self.assertEqual(target.get_nflog_threshold(), 10)
            elif rulenum == 2:
                target = rule.get_target()
                self.assertTrue(isinstance(target, NFLogTarget))
                self.assertEqual(target.get_nflog_prefix(), "hello there ")
            elif rulenum == 3:
                target = rule.get_target()
                self.assertTrue(isinstance(target, NFLogTarget))
                self.assertEqual(target.get_nflog_prefix(), "invalid state \\\"xyz\\\"")
            elif rulenum == 4:
                target = rule.get_target()
                self.assertTrue(isinstance(target, NFLogTarget))
                self.assertEqual(target.get_nflog_prefix(), "nflog-group")
                self.assertEqual(target.get_nflog_group(), 100)
                self.assertEqual(target.get_nflog_size(), 42)
            elif rulenum == 5:
                target = rule.get_target()
                self.assertTrue(isinstance(target, NFLogTarget))
                self.assertEqual(target.get_nflog_prefix(), "tricky nflog-prefix \\\" ")
                self.assertEqual(target.get_nflog_group(), 100)
                self.assertEqual(target.get_nflog_size(), 42)

    def test_parsing_reject_target(self):
        """Parse output with REJECT target
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
     144    57620 REJECT     all  --  *      *       0.0.0.0/0            0.0.0.0/0           reject-with icmp-host-unreachable
  520139 23069461 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        rule = next(iter(input_chain))
        target = rule.get_target()
        self.assertTrue(isinstance(target, RejectTarget))
        self.assertEqual(target.get_rejection_message(),
                                'icmp-host-unreachable')

    def test_parsing_mark_target(self):
        """Parse output with MARK target
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
    0     0 MARK       all  --  *      *       0.0.0.0/0            0.0.0.0/0           MARK set 0xf
    0     0 MARK       all  --  *      *       0.0.0.0/0            0.0.0.0/0           MARK xset 0x11/0xffff0011
    0     0 MARK       all  --  *      *       0.0.0.0/0            0.0.0.0/0           MARK xor 0xf
    0     0 MARK       all  --  *      *       0.0.0.0/0            0.0.0.0/0           MARK or 0xf
    0     0 MARK       all  --  *      *       0.0.0.0/0            0.0.0.0/0           MARK and 0xff
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        input_chain = pft.get_builtin_chain('INPUT')
        for rule in input_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                # Verify SET
                target = rule.get_target()
                self.assertTrue(isinstance(target, MarkTarget))
                self.assertEqual(target.get_op(), MarkTarget.SET)
                self.assertEqual(target.get_mark(), 0xf)
            elif rulenum == 2:
                # Verify XSET
                target = rule.get_target()
                self.assertTrue(isinstance(target, MarkTarget))
                self.assertEqual(target.get_op(), MarkTarget.XSET)
                self.assertEqual(target.get_mark(), 0x11)
                self.assertEqual(target.get_mask(), 0xffff0011)
            elif rulenum == 3:
                # Verify XOR
                target = rule.get_target()
                self.assertTrue(isinstance(target, MarkTarget))
                self.assertEqual(target.get_op(), MarkTarget.XOR)
                self.assertEqual(target.get_mask(), 0xf)
            elif rulenum == 4:
                # Verify OR
                target = rule.get_target()
                self.assertTrue(isinstance(target, MarkTarget))
                self.assertEqual(target.get_op(), MarkTarget.OR)
                self.assertEqual(target.get_mask(), 0xf)
            elif rulenum == 5:
                # Verify AND
                target = rule.get_target()
                self.assertTrue(isinstance(target, MarkTarget))
                self.assertEqual(target.get_op(), MarkTarget.AND)
                self.assertEqual(target.get_mask(), 0xff)

    def test_parsing_connmark_target(self):
        """Parse output with CONNMARK target
        """
        output = ("""\
Chain PREROUTING (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
  558864 28503489 CONNMARK   all  --  *      *       0.0.0.0/0            0.0.0.0/0           connmark match 0x0 CONNMARK set 0x11
  558864 28503489 CONNMARK   all  --  *      *       0.0.0.0/0            0.0.0.0/0           connmark match 0x0 CONNMARK save nfmask 0xfffff ctmask ~0x1f
  558864 28503489 CONNMARK   all  --  *      *       0.0.0.0/0            0.0.0.0/0           connmark match 0x0 CONNMARK restore ctmask 0x1f nfmask ~0xfffff
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT + '\n' +
                self.EMPTY_INPUT + '\n' + self.EMPTY_POSTROUTING)
        pft = IptablesPacketFilterTable('mangle')
        self.assertTrue(pft.init_from_output(output))
        prerouting_chain = pft.get_builtin_chain('PREROUTING')
        self.assertEqual(prerouting_chain.get_rule_count(), 3)
        for rule in prerouting_chain:
            rulenum = rule.get_rulenum()
            if rulenum == 1:
                target = rule.get_target()
                self.assertTrue(isinstance(target, ConnmarkTarget))
                self.assertEqual(target.get_mark(), 0x11)
            elif rulenum == 2:
                target = rule.get_target()
                self.assertTrue(isinstance(target, ConnmarkTarget) and
                                target.is_saving_mark())
                self.assertEqual(target.get_nfmask(), 0xfffff)
                self.assertEqual(target.get_ctmask(), 0x1f)
            elif rulenum == 3:
                target = rule.get_target()
                self.assertTrue(isinstance(target, ConnmarkTarget) and
                                target.is_restoring_mark())
                self.assertEqual(target.get_nfmask(), 0xfffff)
                self.assertEqual(target.get_ctmask(), 0x1f)

    def test_parsing_ttl_target(self):
        """Parse output with TTL target
        """
        output = ("""\
Chain PREROUTING (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 TTL        all  --  *      *       0.0.0.0/0            0.0.0.0/0           TTL set to 10
       0        0 TTL        tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           TTL increment by 1
       0        0 TTL        udp  --  *      *       0.0.0.0/0            0.0.0.0/0           TTL decrement by 2
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT + '\n' +
                self.EMPTY_INPUT + '\n' + self.EMPTY_POSTROUTING)
        pft = IptablesPacketFilterTable('mangle')
        self.assertTrue(pft.init_from_output(output))
        prerouting_chain = pft.get_builtin_chain('PREROUTING')
        for rule in prerouting_chain:
            rulenum = rule.get_rulenum()
            target = rule.get_target()
            if rulenum == 1:
                self.assertTrue(isinstance(target, TtlTarget) and
                                target.get_ttl_value() == 10)
            elif rulenum == 2:
                self.assertTrue(isinstance(target, TtlTarget) and
                                target.get_ttl_inc() == 1)
            elif rulenum == 3:
                target = rule.get_target()
                self.assertTrue(isinstance(target, TtlTarget) and
                                target.get_ttl_dec() == 2)

    def test_parsing_snat_target(self):
        """Parse output with SNAT target
        """
        output = (self.EMPTY_PREROUTING + '\n' + """\
Chain POSTROUTING (1 references)
    pkts      bytes target     prot opt in     out     source               destination
  466007 51946882 SNAT       all  --  *      eth1    0.0.0.0/0            0.0.0.0/0           to:10.10.10.18
""" + '\n' + self.EMPTY_OUTPUT)
        pft = IptablesPacketFilterTable('nat')
        self.assertTrue(pft.init_from_output(output))
        postrouting_chain = pft.get_builtin_chain('POSTROUTING')
        rule = next(iter(postrouting_chain))
        target = rule.get_target()
        self.assertEqual(target.get_target_name(), 'SNAT')
        self.assertEqual(target.get_address(), IPv4Address('10.10.10.18'))

    def test_parsing_masquerade_target(self):
        """Parse output with MASQUERADE target
        """
        output = (self.EMPTY_PREROUTING + '\n' + """\
Chain POSTROUTING (1 references)
    pkts      bytes target     prot opt in     out     source               destination
       0        0 MASQUERADE  all  --  *      *       0.0.0.0/0            0.0.0.0/0
       0        0 MASQUERADE  all  --  *      *       0.0.0.0/0            0.0.0.0/0           random
       0        0 MASQUERADE  tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           masq ports: 2000
       0        0 MASQUERADE  udp  --  *      *       0.0.0.0/0            0.0.0.0/0           udp spts:1000:2000 masq ports: 2000 random
       0        0 MASQUERADE  udp  --  *      *       0.0.0.0/0            0.0.0.0/0           udp spts:1000:2000 masq ports: 20000-30000
       0        0 MASQUERADE  all  --  *      *       0.0.0.0/0            0.0.0.0/0           random-fully
""" + '\n' + self.EMPTY_OUTPUT)
        pft = IptablesPacketFilterTable('nat')
        self.assertTrue(pft.init_from_output(output))
        postrouting_chain = pft.get_builtin_chain('POSTROUTING')
        self.assertEqual(postrouting_chain.get_rule_count(), 6)
        for rule in postrouting_chain:
            rulenum = rule.get_rulenum()
            target = rule.get_target()
            if rulenum == 1:
                self.assertTrue(isinstance(target, MasqueradeTarget))
            elif rulenum == 2:
                self.assertTrue(isinstance(target, MasqueradeTarget) and
                                target.uses_random_port_mapping())
            elif rulenum == 3:
                self.assertTrue(isinstance(target, MasqueradeTarget) and
                                target.get_ports() == (2000, None))
            elif rulenum == 4:
                self.assertTrue(isinstance(target, MasqueradeTarget) and
                            target.get_ports() == (2000, None) and
                                target.uses_random_port_mapping())
            elif rulenum == 5:
                self.assertTrue(isinstance(target, MasqueradeTarget) and
                                target.get_ports() == (20000, 30000))
            if rulenum == 6:
                self.assertTrue(isinstance(target, MasqueradeTarget) and
                        target.uses_fully_random_port_mapping())

    def test_parsing_notrack_target(self):
        """Parse output with NOTRACK target
        """
        output = (self.EMPTY_PREROUTING + '\n' + """\
Chain OUTPUT (policy ACCEPT 12 packets, 1845 bytes)
 pkts bytes target     prot opt in     out     source               destination
    0     0 NOTRACK    tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           tcp dpt:55555
""")
        pft = IptablesPacketFilterTable('raw')
        self.assertTrue(pft.init_from_output(output))
        output_chain = pft.get_builtin_chain('OUTPUT')
        rule = next(iter(output_chain))
        target = rule.get_target()
        self.assertTrue(isinstance(target, NoTrackTarget))

    def test_parsing_trace_target(self):
        """Parse output with TRACE target
        """
        output = (self.EMPTY_PREROUTING + '\n' + """\
Chain OUTPUT (policy ACCEPT 12 packets, 1845 bytes)
 pkts bytes target     prot opt in     out     source               destination
    0     0 TRACE      tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           tcp dpt:55555
""")
        pft = IptablesPacketFilterTable('raw')
        self.assertTrue(pft.init_from_output(output))
        output_chain = pft.get_builtin_chain('OUTPUT')
        rule = next(iter(output_chain))
        target = rule.get_target()
        self.assertTrue(isinstance(target, TraceTarget))

    def test_parsing_unknown_target(self):
        """Parse output with unknown target
        """
        output = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
196245663 314408786102 prod_INPUT  all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain prod_INPUT (1 references)
    pkts      bytes target     prot opt in     out     source               destination
    0     0 AUDIT      all  --  *      *       1.2.3.4              0.0.0.0/0           AUDIT accept
""" + '\n' + self.EMPTY_FORWARD + '\n' + self.EMPTY_OUTPUT
        pft = IptablesPacketFilterTable('filter')
        init_ok = pft.init_from_output(output, log_parsing_failures=False)
        self.assertFalse(init_ok, 'failed bad output')



class TestTargetGeneration(unittest.TestCase):
    """Test generation of iptables arguments for targets
    """

    def test_mark_target_args(self):
        """iptables argument generation for the MARK target
        """
        # test no args
        target = MarkTarget()
        self.assertRaises(IptablesError, target.to_iptables_args)
        # test attempt to double-set
        target = MarkTarget(10)
        self.assertRaises(IptablesError, target.and_mark, 0xff)
        # test set via constructor
        target = MarkTarget(10)
        self.assertEqual(target.to_iptables_args(), ['MARK', '--set-mark', '0xa'])
        # test the various setter methods
        target = MarkTarget().set_mark(10, 0xffff)
        self.assertEqual(target.to_iptables_args(), ['MARK', '--set-mark', '0xa/0xffff'])
        target = MarkTarget().set_xmark(20, 0xffff)
        self.assertEqual(target.to_iptables_args(), ['MARK', '--set-xmark', '0x14/0xffff'])
        target = MarkTarget().and_mark(0xffff)
        self.assertEqual(target.to_iptables_args(), ['MARK', '--and-mark', '0xffff'])
        target = MarkTarget().xor_mark(0xffff)
        self.assertEqual(target.to_iptables_args(), ['MARK', '--xor-mark', '0xffff'])
        target = MarkTarget().or_mark(0xffff)
        self.assertEqual(target.to_iptables_args(), ['MARK', '--or-mark', '0xffff'])

    def test_set_target_args(self):
        """iptables argument generation for the SET target
        """
        ipset_name = "fooset"
        ipset_flags = ["src"]
        target = SetTarget(SetTarget.ADD_SET, ipset_name, ipset_flags, exist=True)
        self.assertEqual(target.to_iptables_args(),
                        ['SET', '--add-set', ipset_name, ",".join(ipset_flags), "--exist"])


class TestPrefix(unittest.TestCase):
    """Test chain prefix handling
    """

    GOOD_OUTPUT = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
129651288 230406442471 prod_INPUT  all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain FORWARD (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
378613942 278529707859 prod_FORWARD  all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain OUTPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
62441650 9685307040 prod_OUTPUT  all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain prod_FORWARD (1 references)
    pkts      bytes target     prot opt in     out     source               destination
377452936 278361749795 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain prod_INPUT (1 references)
    pkts      bytes target     prot opt in     out     source               destination
128158511 230312235930 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain prod_OUTPUT (1 references)
    pkts      bytes target     prot opt in     out     source               destination
55238105 5261597979 ACCEPT  all  --  *      eth1    0.0.0.0/0            0.0.0.0/0
"""

    def test_creating_table_using_prefix(self):
        """Parse valid output with no errors when a prefix is specified
        """
        prefix = 'prod_'
        pft = IptablesPacketFilterTable('filter', chain_prefix=prefix)
        init_ok = pft.init_from_output(self.GOOD_OUTPUT)
        self.assertTrue(init_ok)
        for chain in pft.get_user_chains():
            self.assertTrue(chain.get_real_name().startswith(prefix))

    def test_creating_table_using_nonexistent_prefix(self):
        """Create a table using non-existent prefix
        """
        pft = IptablesPacketFilterTable('filter', chain_prefix='foo_')
        init_ok = pft.init_from_output(self.GOOD_OUTPUT)
        self.assertTrue(init_ok)

    def test_prefix_setting(self):
        """Check that setting the prefix works
        """
        pft = IptablesPacketFilterTable('filter')
        init_ok = pft.init_from_output(self.GOOD_OUTPUT)
        self.assertTrue(init_ok)
        chain_map_copy = pft.get_chain_map().copy()
        prefix = 'prod_'
        pft.set_prefix('prod_')
        for chain in pft.get_user_chains():
            self.assertTrue(chain.get_real_name().startswith(prefix))
        pft.set_prefix(None)
        self.assertTrue(chain_map_copy == pft.get_chain_map())


class TestMiscellaneous(unittest.TestCase):
    """Test miscellaneous operations
    """

    GOOD_OUTPUT = """\
Chain INPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
129651288 230406442471 prod_INPUT  all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain FORWARD (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
378613942 278529707859 prod_FORWARD  all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain OUTPUT (policy DROP 0 packets, 0 bytes)
    pkts      bytes target     prot opt in     out     source               destination
62441650 9685307040 prod_OUTPUT  all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain prod_FORWARD (1 references)
    pkts      bytes target     prot opt in     out     source               destination
377452936 278361749795 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain prod_INPUT (1 references)
    pkts      bytes target     prot opt in     out     source               destination
128158511 230312235930 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain prod_OUTPUT (1 references)
    pkts      bytes target     prot opt in     out     source               destination
55238105 5261597979 ACCEPT  all  --  *      eth1    0.0.0.0/0            0.0.0.0/0
"""

    def test_epoch(self):
        """Check that the epoch is initialized properly
        """
        pft = IptablesPacketFilterTable('filter')
        for i in range(1, 3):
            init_ok = pft.init_from_output(self.GOOD_OUTPUT)
            self.assertTrue(init_ok)
            self.assertEqual(pft.get_epoch(), i)

    def test_zero_counters(self):
        """Test that the correct command is issued to zero counters
        """
        runner = SimulatedIptablesRun(0, None)
        pft = IptablesPacketFilterTable('filter', runner=runner)
        init_ok = pft.init_from_output(self.GOOD_OUTPUT)
        self.assertTrue(init_ok)
        #
        # Zero the counters of a specific chain
        #
        chain = pft.get_builtin_chain('FORWARD')
        rule = next(iter(chain))
        rule.zero_counters()
        expected_cmd = ['iptables', '-t', 'filter', '-Z', 'FORWARD', '1']
        commands = runner.get_run()
        self.assertEqual(commands[0].cmd, expected_cmd)
        #
        # Zero the counters of a specific chain
        #
        runner.clear_run()
        chain = pft.get_builtin_chain('OUTPUT')
        chain.zero_counters()
        expected_cmd = ['iptables', '-t', 'filter', '-Z', 'OUTPUT']
        commands = runner.get_run()
        self.assertEqual(commands[0].cmd, expected_cmd)
        #
        # Zero the counters of all chains
        #
        runner.clear_run()
        pft.zero_counters()
        commands = runner.get_run()
        expected_cmd = ['iptables', '-t', 'filter', '-Z']
        self.assertEqual(commands[0].cmd, expected_cmd)

    def test_counters(self):
        """Test the packet/byte counters
        """
        output = """\
Chain INPUT (policy DROP 10 packets, 500 bytes)
    pkts      bytes target     prot opt in     out     source               destination
    500       50000 fw_INPUT   all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain fw_INPUT (1 references)
    pkts      bytes target     prot opt in     out     source               destination
    400       40000 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0           state RELATED,ESTABLISHED
    100       10000 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain FORWARD (policy DROP 20 packets, 2000 bytes)
    pkts      bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 30 packets, 3000 bytes)
    pkts      bytes target     prot opt in     out     source               destination
"""
        pft = IptablesPacketFilterTable('filter')
        self.assertTrue(pft.init_from_output(output))
        for bltin in pft.get_builtin_chains():
            if bltin.get_real_name() == 'INPUT':
                self.assertEqual(bltin.get_policy(), Targets.DROP)
                self.assertEqual(bltin.get_policy_packet_count(), 10)
                self.assertEqual(bltin.get_policy_byte_count(), 500)
                self.assertEqual(bltin.get_packet_count(), 510)
                self.assertEqual(bltin.get_byte_count(), 50500)
            elif bltin.get_real_name() == 'FORWARD':
                self.assertEqual(bltin.get_policy(), Targets.DROP)
                self.assertEqual(bltin.get_policy_packet_count(), 20)
                self.assertEqual(bltin.get_policy_byte_count(), 2000)
                self.assertEqual(bltin.get_packet_count(), 20)
                self.assertEqual(bltin.get_byte_count(), 2000)
            elif bltin.get_real_name() == 'OUTPUT':
                self.assertEqual(bltin.get_policy(), Targets.ACCEPT)
                self.assertEqual(bltin.get_policy_packet_count(), 30)
                self.assertEqual(bltin.get_policy_byte_count(), 3000)
                self.assertEqual(bltin.get_packet_count(), 30)
                self.assertEqual(bltin.get_byte_count(), 3000)
        chain = pft.get_chain_by_rcn('fw_INPUT')
        self.assertEqual(chain.get_packet_count(), 500)
        self.assertEqual(chain.get_byte_count(), 50000)

    def test_set_policy(self):
        """Test setting the policy of a builtin chain
        """
        runner = SimulatedIptablesRun(0, None)
        pft = IptablesPacketFilterTable('filter', runner=runner)
        init_ok = pft.init_from_output(self.GOOD_OUTPUT)
        self.assertTrue(init_ok)
        chain = pft.get_builtin_chain('OUTPUT')
        chain.set_policy(Targets.DROP)
        expected_cmd = ['iptables', '-t', 'filter', '-P', 'OUTPUT',
                                        Targets.DROP.get_target_name()]
        commands = runner.get_run()
        self.assertEqual(commands[0].cmd, expected_cmd)


class TestChainOperations(unittest.TestCase):
    """Test chain operations.
    """

    @staticmethod
    def _runner(*args, **kwargs):
        """Runner that logs the arguments without invoking iptables(8)
        """
        root_logger.info("Executing: args=%s kwargs=%s", args, kwargs)
        proc = subprocess.CompletedProcess(args, 0)
        proc.stdout = ""
        return proc

    def test_chain_creation_deletion(self):
        """Create, then delete a chain.
        """
        runner = SimulatedIptablesRun(0, None)
        pft = IptablesPacketFilterTable('filter', runner=runner)
        #
        # Chain creation
        #
        chain = pft.create_chain('test_chain')
        commands = runner.get_run()
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].cmd,
                        ['iptables', '-t', 'filter', '-N', 'test_chain'])
        runner.clear_run()
        #
        # Chain deletion
        #
        pft.delete_chain(chain)
        commands = runner.get_run()
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0].cmd,
                        ['iptables', '-t', 'filter', '-F', 'test_chain'])
        self.assertEqual(commands[1].cmd,
                        ['iptables', '-t', 'filter', '-X', 'test_chain'])

    def test_multi_chain_creation_deletion(self):
        """Create 3 chains, with 2 of them jump'ing to the 3rd.
        Then delete the chain that serves as the terget.
        Rules referencing that chain should be automatically removed.
        """
        runner = SimulatedIptablesRun(0, None)
        pft = IptablesPacketFilterTable('filter', runner=runner)
        #
        # Chain creation
        #
        chain1 = pft.create_chain('test_chain_1')
        chain2 = pft.create_chain('test_chain_2')
        chain3 = pft.create_chain('test_chain_3')
        commands = runner.get_run()
        self.assertEqual(len(commands), 3)
        self.assertEqual(commands[0].cmd,
                        ['iptables', '-t', 'filter', '-N', 'test_chain_1'])
        self.assertEqual(commands[1].cmd,
                        ['iptables', '-t', 'filter', '-N', 'test_chain_2'])
        self.assertEqual(commands[2].cmd,
                        ['iptables', '-t', 'filter', '-N', 'test_chain_3'])
        runner.clear_run()
        #
        # Rule creation
        #
        chain2.append_rule(ChainRule(target=ChainTarget(chain=chain1)))
        chain3.append_rule(ChainRule(target=ChainTarget(chain=chain1)))
        commands = runner.get_run()
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0].cmd,
            ['iptables', '-t', 'filter',
                    '-A', 'test_chain_2', '-j', 'test_chain_1'])
        self.assertEqual(commands[1].cmd,
            ['iptables', '-t', 'filter',
                    '-A', 'test_chain_3', '-j', 'test_chain_1'])
        runner.clear_run()
        #
        # The following should trigger the automatic deletion of
        # the rules referencing test_chain_1
        #
        pft.delete_chain(chain1)
        commands = runner.get_run()
        self.assertEqual(len(commands), 4)
        # Since the order of deletion is not guaranteed, allow both
        if commands[0].cmd[4] == 'test_chain_2':
            first_chain = 'test_chain_2'
            second_chain = 'test_chain_3'
        else:
            first_chain = 'test_chain_3'
            second_chain = 'test_chain_2'
        self.assertEqual(commands[0].cmd,
            ['iptables', '-t', 'filter', '-D', first_chain, '1'])
        self.assertEqual(commands[1].cmd,
            ['iptables', '-t', 'filter', '-D', second_chain, '1'])
        self.assertEqual(commands[2].cmd,
                        ['iptables', '-t', 'filter', '-F', 'test_chain_1'])
        self.assertEqual(commands[3].cmd,
                        ['iptables', '-t', 'filter', '-X', 'test_chain_1'])
        self.assertEqual(len(chain2.get_rules()), 0)
        self.assertEqual(len(chain3.get_rules()), 0)

    def test_rule_enumeration(self):
        """Rule enumeration
        """
        runner = SimulatedIptablesRun(0, None)
        pft = IptablesPacketFilterTable('filter', runner=runner)
        #
        # We create the following structure:
        #
        #  jump_target:
        #  goto_target:
        #  caller_chain:
        #       -m owner --uid-owner 10 --gid-owner 1 -j RETURN (1 match)
        #       -p tcp --dport 22 -j jump_target                (2 matches, chain-target)
        #       -p tcp -j DROP                                  (1 match)
        #       -p udp -g goto_target                           (1 match, chain-target-goto)
        #       -j jump_target                                  (0 matches, chain-target)
        #
        jump_target = pft.create_chain('jump_target')
        goto_target = pft.create_chain('goto_target')
        chain = pft.create_chain('caller_chain')
        chain.append_rule(ChainRule(
                match=OwnerMatch().uid().equals(10).gid().equals(1),
                target=Targets.RETURN))
        chain.append_rule(ChainRule(
                match_list=[
                        PacketMatch().protocol().equals('tcp'),
                        TcpMatch().dest_port().equals(22),
                        ],
                target=ChainTarget(chain=jump_target)))
        chain.append_rule(ChainRule(
                match=PacketMatch().protocol().equals('tcp'),
                target=Targets.DROP))
        chain.append_rule(ChainRule(
                match=PacketMatch().protocol().equals('udp')
                        ).go_to(chain=goto_target))
        chain.append_rule(ChainRule(
                target=ChainTarget(chain=jump_target)))
        #
        # 3 rules target chains
        #
        rules_to_chains = list(chain.iter_rules(chain_target=True))
        self.assertEqual(len(rules_to_chains), 3)
        #
        # 1 rule uses goto
        #
        rules_go_to_chains = list(chain.iter_rules(uses_goto=True))
        self.assertEqual(len(rules_go_to_chains), 1)
        #
        # 3 rules with a single match
        #
        single_match_rules = list(chain.iter_rules(match_count=1))
        self.assertEqual(len(single_match_rules), 3)
        #
        # 1 rule with a single match and a chain target
        #
        single_match_rules_to_chains = list(
                chain.iter_rules(chain_target=True, match_count=1))
        self.assertEqual(len(single_match_rules_to_chains), 1)
        #
        # 1 rule with a match for TCP dest port 22
        #
        port22_rules = list(chain.iter_rules(match=TcpMatch().dest_port().equals(22)))
        self.assertEqual(len(port22_rules), 1)
        #
        # 1 rule with a PacketMatch that uses goto
        #
        packet_goto_rules = list(chain.iter_rules(match=PacketMatch(), uses_goto=True))
        self.assertEqual(len(packet_goto_rules), 1)
        #
        # 1 rule with a match with 2 criteria
        #
        rules = list(chain.iter_rules(match=OwnerMatch().uid().any().gid().equals(1)))
        self.assertEqual(len(rules), 1)

    def test_rule_operations(self):
        """Rule search, deletion
        """
        runner = SimulatedIptablesRun(0, None)
        pft = IptablesPacketFilterTable('filter', runner=runner)
        #
        # We create the following structure:
        #  test_chain_1:
        #  test_chain_2:
        #       -p tcp -j test_chain_3
        #       -j test_chain_1
        #  test_chain_3:
        #       -p udp -j test_chain_2
        #       -j test_chain_1
        #
        chain1 = pft.create_chain('test_chain_1')
        chain2 = pft.create_chain('test_chain_2')
        chain3 = pft.create_chain('test_chain_3')
        chain2.append_rule(ChainRule(
            match=PacketMatch().protocol().equals('tcp')).jump_to(chain=chain3))
        chain2.append_rule(ChainRule(target=ChainTarget(chain=chain1)))
        chain3.append_rule(ChainRule(
            match=PacketMatch().protocol().equals('udp')).jump_to(chain=chain2))
        chain3.append_rule(ChainRule(target=ChainTarget(chain=chain1)))
        commands = runner.get_run()
        self.assertEqual(commands[0].cmd,
                        ['iptables', '-t', 'filter', '-N', 'test_chain_1'])
        self.assertEqual(commands[1].cmd,
                        ['iptables', '-t', 'filter', '-N', 'test_chain_2'])
        self.assertEqual(commands[2].cmd,
                        ['iptables', '-t', 'filter', '-N', 'test_chain_3'])
        self.assertEqual(commands[3].cmd,
            ['iptables', '-t', 'filter',
                    '-A', 'test_chain_2', '-p', 'tcp', '-j', 'test_chain_3'])
        self.assertEqual(commands[4].cmd,
            ['iptables', '-t', 'filter',
                    '-A', 'test_chain_2', '-j', 'test_chain_1'])
        self.assertEqual(commands[5].cmd,
            ['iptables', '-t', 'filter',
                    '-A', 'test_chain_3', '-p', 'udp', '-j', 'test_chain_2'])
        self.assertEqual(commands[6].cmd,
            ['iptables', '-t', 'filter',
                    '-A', 'test_chain_3', '-j', 'test_chain_1'])
        #
        # Since there are 2 chains that have one rule each jumping
        # to test_chain_1, the result should be a list containing 2 lists,
        # with each of those lists containing a single rule.
        #
        result = pft.get_rules_by_target(
                        ChainTarget(real_chain_name='test_chain_1'))
        self.assertEqual(len(result), 2)
        for rule_list in result:
            self.assertEqual(len(rule_list), 1)
            rule = rule_list[0]
            owner = rule.get_chain()
            self.assertTrue(owner is chain2 or owner is chain3)
        #
        # Search by match
        #
        rules = chain2.find_rule_by(match=MatchNone())
        self.assertTrue(len(rules), 1)
        rule = rules[0]
        self.assertTrue(rule.get_rulenum(), 2)
        target = rule.get_target()
        self.assertTrue(isinstance(target, ChainTarget))
        self.assertTrue(target.get_chain() is chain1)
        #
        # Search by match (2)
        #
        rules = chain3.find_rule_by(
                        match=PacketMatch().protocol().equals('udp'))
        self.assertTrue(len(rules), 1)
        rule = rules[0]
        self.assertTrue(rule.get_rulenum(), 1)
        target = rule.get_target()
        self.assertTrue(isinstance(target, ChainTarget))
        self.assertTrue(target.get_chain() is chain2)
        #
        # Search by target
        #
        rules = chain3.find_rule_by(target=ChainTarget(chain=chain1))
        self.assertTrue(len(rules), 1)
        rule = rules[0]
        self.assertTrue(rule.get_rulenum(), 2)
        target = rule.get_target()
        self.assertTrue(isinstance(target, ChainTarget))
        self.assertTrue(target.get_chain() is chain1)
        #
        # Search by match and target
        #
        rules = chain3.find_rule_by(
                        match=PacketMatch().protocol().equals('udp'),
                        target=ChainTarget(chain=chain2))
        self.assertTrue(len(rules), 1)
        rule = rules[0]
        self.assertTrue(rule.get_rulenum(), 1)
        target = rule.get_target()
        self.assertTrue(isinstance(target, ChainTarget))
        self.assertTrue(target.get_chain() is chain2)
        runner.clear_run()
        #
        # Delete the first rule of test_chain_3
        #
        n_deleted = chain3.delete_rule_if(
                        match=PacketMatch().protocol().equals('udp'),
                        target=ChainTarget(chain=chain2))
        self.assertTrue(n_deleted, 1)
        commands = runner.get_run()
        self.assertTrue(commands[0].cmd,
                ['iptables', '-t', 'filter', '-D', 'test_chain_3', 1])

    def test_chain_rule_ownership(self):
        """Attempt to insert a rule into a chain twice.
        The 2nd attempt should fail as the rule already has an owner.
        """
        pft = IptablesPacketFilterTable('filter', runner=self._runner)
        chain = pft.create_chain('test_chain')
        rule = ChainRule(target=Targets.ACCEPT)
        chain.append_rule(rule)
        self.assertRaises(IptablesError, lambda: chain.append_rule(rule))
        # Remove the rule, verify it now has no owner
        chain.flush()
        self.assertTrue(rule.get_chain() is None)
        chain.append_rule(rule)
        # Delete it by rule number
        chain.delete_rulenum(rule.get_rulenum())
        self.assertTrue(rule.get_chain() is None)

    def test_chain_rule_numbering(self):
        """Verify rule numbering when rules are inserted/deleted.
        """
        pft = IptablesPacketFilterTable('filter', runner=self._runner)
        chain = pft.create_chain('test_chain')
        rule_list = []
        # Always inserting as rule #1 forces previously inserted
        # rules to be renumbered.
        for i in range(4):
            rule = ChainRule(target=Targets.ACCEPT)
            chain.insert_rule(rule, rulenum=1)
            rule_list.append(rule)
        for i in range(4):
            expected_num = 4-i
            self.assertEqual(rule_list[i].get_rulenum(), expected_num)

    def test_chain_rule_indexing(self):
        """Verify chain rule indexing
        """
        pft = IptablesPacketFilterTable('filter', runner=self._runner)
        chain = pft.create_chain('test_chain')
        rule_list = []
        # Always inserting as rule #1 forces previously inserted
        # rules to be renumbered.
        for i in range(4):
            rule = ChainRule(target=Targets.ACCEPT)
            chain.insert_rule(rule, rulenum=1)
            rule_list.append(rule)
        self.assertEqual(len(chain), 4)
        for rule in chain:
            self.assertTrue(rule is chain[rule.get_rulenum()])
        num_rules = len(chain)
        for i in range(num_rules):
            rule = chain[i-num_rules]
            self.assertEqual(rule.get_rulenum(), i+1)


if __name__ == '__main__':
    unittest.main()
