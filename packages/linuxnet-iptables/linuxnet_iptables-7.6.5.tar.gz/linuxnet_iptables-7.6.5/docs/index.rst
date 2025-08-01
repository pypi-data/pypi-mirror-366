..
    Copyright (c) 2022, 2023, 2024, Panagiotis Tsirigotis
    
    This file is part of linuxnet-iptables.
    
    linuxnet-iptables is free software: you can redistribute it and/or
    modify it under the terms of version 3 of the GNU Affero General Public
    License as published by the Free Software Foundation.
    
    linuxnet-iptables is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
    License for more details.
    
    You should have received a copy of the GNU Affero General
    Public License along with linuxnet-iptables. If not, see
    <https://www.gnu.org/licenses/>.

linuxnet-iptables: a Python package for managing Linux packet filtering
=========================================================================

Release v\ |version|.

**linuxnet-iptables** provides programmatic access to the
Linux **iptables(8)** (or **ip6tables(8)**) command.
Using **linuxnet-iptables** one can view and manipulate existing rules
or create new rules.

The following code shows all rules of the **INPUT** chain; the code must be run
as root since the **iptables(8)** command requires root privileges (the output
will probably be different on your system)::

    >>> from linuxnet.iptables import IptablesPacketFilterTable
    >>> table = IptablesPacketFilterTable('filter')
    >>> table.read_system_config()
    True
    >>> input_chain = table.get_chain('INPUT')
    >>> for rule in input_chain:
    ...    print(' '.join(rule.to_iptables_args()))
    ...
    -j prod_bad_traffic
    -m state --state RELATED,ESTABLISHED -j ACCEPT
    -j prod_ingress
    -j prod_lsvc
    -j prod_INPUT_ldrop
    >>>
    >>> print(input_chain.get_packet_count())
    183506560
    >>>

Creating a new chain (continuing from above)::

    >>> from linuxnet.iptables import ChainRule, Targets
    >>> newchain = table.create_chain('acceptall')
    >>> newchain.append_rule(ChainRule(target=Targets.ACCEPT))

Verifying the new chain has been created::

    # iptables -n -L acceptall
    Chain acceptall (0 references)
    target     prot opt source               destination
    ACCEPT     all  --  0.0.0.0/0            0.0.0.0/0

Modifying the new chain to only accept TCP packets::

    >>> newchain.flush()        # remove the existing rule
    >>> from linuxnet.iptables import PacketMatch
    >>> match_tcp = PacketMatch().protocol().equals('tcp')
    >>> rule = ChainRule(match=match_tcp, target=Targets.ACCEPT)
    >>> newchain.append_rule(rule)
    >>> newchain.append_rule(ChainRule(target=Targets.DROP))

Verifying the new chain has been updated::

    # iptables -n -L acceptall
    Chain acceptall (0 references)
    target     prot opt source               destination
    ACCEPT     tcp  --  0.0.0.0/0            0.0.0.0/0
    DROP       all  --  0.0.0.0/0            0.0.0.0/0

Deleting the new chain::

    >>> table.delete_chain(newchain)

Verifying the new chain has been deleted::

    # iptables -n -L acceptall
    iptables: No chain/target/match by that name.


API Documentation
-----------------

.. toctree::
   :maxdepth: 3
   :includehidden:

   iptables_api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
