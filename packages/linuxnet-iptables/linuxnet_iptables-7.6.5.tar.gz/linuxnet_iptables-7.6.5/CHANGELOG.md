Change Log
==========

7.6.5 (2025-07-31)
------------------

- added support for the --log-macdecode option of the LOG target


7.6.3 (2025-07-30)
------------------

- added SetTarget class to support the SET target


7.4.4 (2024-08-18)
------------------

- bugfix in PacketMatch class (iptables output parsing)


7.4.1 (2024-07-30)
------------------

- added NFLogTarget class
- added LengthMatch class
- added ConnbytesMatch class


7.0.3 (2024-04-06)
------------------

- comparison value used in SourceAddressCriterion/DestAddressCriterion
  may be specified as a IPv4Address/IPv6Address or as a string (in
  addition to IPv4Network/IPv6Network)


7.0.0 (2024-03-21)
------------------

- added IPv6 support; the PacketMatch, ConntrackMatch, SnatTarget, DnatTarget
  classes now support both IPv4 and IPv6 addresses
- SnatTarget now supports the --random-fully option of the SNAT target
- this version maintains user API backwards-compatibility;
  however the major version was changed because the Target class
  implementation was updated in a way that breaks backwards-compatibility
  with out-of-tree Target subclasses


6.8.3 (2024-01-24)
------------------

- added MultiportMatch class


6.7.0 (2023-10-21)
------------------

- added MacMatch class


6.6.0 (2023-09-08)
------------------

- added SetMatch class
- added StatisticMatch class
- added support for the --random-fully option of the MASQUERADE target
- improved handling of all-upper-case chain names


6.5.0 (2023-08-20)
------------------

- owner match now supports for the --suppl-groups option
- conntrack match now supports the options --ctdir, --ctorigsrc,
  --ctorigdst, --ctreplsrc, --ctrepldst, --ctorigsrcport,
  --ctorigdstport, --ctreplsrcport, --ctrepldstport, --ctexpire


6.4.5 (2023-07-24)
------------------

- RecentMatch now supports the --mask and --reap options
- ProtocolCriterion now also accepts protocols specified as numbers
- Chain class now supports special methods __len__ and __getitem__


6.3.1 (2023-07-13)
------------------

- added RecentMatch class
- added ChainRule.iter_matches()
- added GenericPositiveCriterion class for criteria that do
  not support inequality comparisons


6.1.0 (2023-07-09)
------------------

- this version maintains user API backwards-compatibility;
  however the major version was changed because the Match/Criterion
  implementation was updated in a way that breaks
  backwards-compatibility with out-of-tree Match subclasses
- the Chain and ChainRule classes are now iterable
- added ability to zero the packet/byte counters of individual rules
- the Chain.iter_rules() can now return rules that match a number of
  conditions: have a chain as a target, have a specific match, etc.
- added support for TCP option matching (--tcp-option) to TcpMatch


5.4.0 (2023-06-18)
------------------

- added AddressTypeMatch class to support the 'addrtype' match
- added Chain.has_rules() method

5.3.0 (2023-06-04)
------------------

- added Chain.iter_rules() method
- removed use of distutils from setup.py

5.2.0 (2023-06-03)
------------------

- added NoTrackTarget class to support the iptables NOTRACK target
- added TraceTarget class to support the iptables TRACE target

5.0.4 (2023-03-05)
------------------

- bugfixes in ConnmarkTarget class

5.0.2 (2023-03-01)
------------------

- major version updated due to changes to the Chain class:
    * the Chain methods that were only applicable to builtin chains
      were moved to the new BuiltinChain class (which is a subclass
      of Chain)
    * the Chain.__init__() signature changed, however this does not
      affect code that only specified a chain name when creating a
      Chain instance
    * the Chain methods set_pft/clear_pft were renamed to
      _set_pft/_clear_pft
- added support for setting the policy of a builtin chain
- added support for the 'security' table

4.3.1 (2023-02-20)
------------------

- Added method to Chain/IptablesPacketFilterTable class to zero the packet/byte
  counters of a specific chain, or all chains

4.2.1 (2023-02-07)
------------------

- Fixed bug in LogTarget class

4.2.0 (2023-02-06)
------------------

- added framework for extending the linuxnet.iptables package
  with new xxxMatch and xxxTarget classes to support additional
  iptables match and target extensions
- added new section in the documentation with information
  on how to add new match/target classes (including examples)
- reworked package module structure:
    * monolithic match.py module broken into per-match-class modules
    * monolithic target.py module broken into per-target-class modules
- all CONNMARK target options are now supported
- added support for 'owner' match
- added mask support in MarkMatch and ConnmarkMatch classes
- the IcmpTypeCriterion now supports the complete list of ICMP types
  and ICMP codes
- The following changes were backwards-incompatible, and resulted
  in the bumpting of the major version number:
    * the xxxCriterion classes are no longer in the linuxnet.iptables
      namespace
    * the Criterion.equals() method is no longer implemented
    * the MssCriterion value changed from a string to a tuple of integers
    * the RateLimitCriterion value changed from integer to a
      LimitMatch.Rate object
    * the RateLimitCriterion rate2spec and spec2rate methods were removed
    * replaced the LogTarget.set_log_options() method with
      option-specific methods

3.2.0 (2023-01-27)
------------------

- Improved MARK/CONNMARK target support
- Reworked documentation

3.1.0 (2023-01-21)
------------------

- Added support for the TTL target
- Added support for the TTL match

3.0.1 (2022-12-31)
------------------

- First published release

