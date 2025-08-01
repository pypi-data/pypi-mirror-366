# linuxnet-iptables

**linuxnet-iptables** provides programmatic access to the
Linux `iptables(8)` (or `ip6tables(8)`) command.
Using **linuxnet-iptables** one can view existing chains/rules,
create new ones, or delete existing ones.
The package documentation is available
[here](https://linuxnet-iptables.readthedocs.io/en/latest/index.html).

For the following examples, Python3 (3.6 or later) is required.

```python
>>> from linuxnet.iptables import IptablesPacketFilterTable
>>> table = IptablesPacketFilterTable('filter')
>>> table.read_system_config()
>>> input_chain = table.get_chain('INPUT')
>>> for rule in input_chain:
...    print(' '.join(rule.to_iptables_args()))
...
-j prod_bad_traffic
-m state --state RELATED,ESTABLISHED -j ACCEPT
-j prod_ingress
-j prod_INPUT_ldrop
>>>
>>> print(input_chain.get_packet_count())
183506560
>>>
```

The above code requires root access in order to successfully invoke the
`iptables` command. If you are uncomfortable running it as root, you can
extract the `iptables` output as root and then process it with
**linuxnet-iptables** (note that the **-xnv** options **must** be
specified):

```console
# iptables -xnv -L > /tmp/iptables.output
#
```

Then, as a regular user:

```python
>>> with open("/tmp/iptables.output") as f:
...    output = f.read()
...
>>> from linuxnet.iptables import IptablesPacketFilterTable
>>> table = IptablesPacketFilterTable('filter')
>>> table.init_from_output(output)
True
>>> input_chain = table.get_chain('INPUT')
>>> for rule in input_chain:
...     print(' '.join(rule.to_iptables_args()))
...
-j prod_bad_traffic
-m state --state RELATED,ESTABLISHED -j ACCEPT
-j prod_ingress
-j prod_INPUT_ldrop
>>>
```

Modifications to the chains are also supported as shown in the
following (hereon, root permissions will be assumed).

Creating a new chain:

```python
>>> from linuxnet.iptables import ChainRule, Targets
>>> newchain = table.create_chain('acceptall')
>>> newchain.append_rule(ChainRule(target=Targets.ACCEPT))
>>>
```

```console
# iptables -nv -L acceptall
Chain acceptall (0 references)
 pkts bytes target     prot opt in     out     source               destination
    0     0 ACCEPT     all  --  *      *       0.0.0.0/0            0.0.0.0/0
#
```

Modifying the new chain to only accept TCP packets:

```python
>>> newchain.flush()        # remove the existing rule
>>> from linuxnet.iptables import PacketMatch
>>> match_tcp = PacketMatch().protocol().equals('tcp')
>>> rule = ChainRule(match=match_tcp, target=Targets.ACCEPT)
>>> newchain.append_rule(rule)
>>> newchain.append_rule(ChainRule(target=Targets.DROP))
>>>
```

```console
# iptables -L acceptall -nv
Chain acceptall (0 references)
 pkts bytes target     prot opt in     out     source               destination
    0     0 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0
    0     0 DROP       all  --  *      *       0.0.0.0/0            0.0.0.0/0
#
```

Deleting the new chain:

```python
>>> table.delete_chain(newchain)
>>>
```


---------------------

# Installation

Python3 is required.

Available `Makefile` targets can be listed by invoking `make` with no arguments.

`make install` will install the package.

`make test` runs the unit tests.

