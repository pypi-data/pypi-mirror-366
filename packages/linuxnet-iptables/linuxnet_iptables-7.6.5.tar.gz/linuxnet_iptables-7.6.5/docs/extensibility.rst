..
    Copyright (c) 2023, 2024, Panagiotis Tsirigotis
    
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

.. currentmodule:: linuxnet.iptables.extension

Extensibility
=============

**linuxnet.iptables** supports only a subset of the match extensions
and rule targets that are available in the Linux kernel.

Additional matches can be supported by subclassing the
:class:`Match` and :class:`Criterion` classes.

Additional targets can be supported by subclassing the
:class:`Target` class.

.. toctree::
    :maxdepth: 2


Supporting a new match
----------------------

Supporting a new **iptables** match requires the addition of a new
:class:`Match` subclasss and one or more :class:`Criterion`
subclasses.  This will be illustrated via example; the example
uses the implementation of the existing :class:`TcpmssMatch` class which
supports the **iptables** **tcpmss** match extension::

    iptables -m tcpmss --mss value

The example code includes the :class:`TcpmssMatch` class and the
associated :class:`MssCriterion` class.

All classes needed for implementing a new match are available in
the **linux.iptables.extension** module.

.. literalinclude:: match-example.py
    :language: python
    :linenos:


Adding a Match subclass
~~~~~~~~~~~~~~~~~~~~~~~

A new :class:`Match` subclass **must** implement the following methods:

#. :meth:`get_match_name`: this method returns the **iptables(8)** match
   extension name

#. :meth:`get_criteria`: this method returns an iterable with the
   new match's criteria

#. :meth:`parse`: this is a classmethod that takes a single argument of type
   :class:`MatchParser` and returns an instance of the new subclass.
   This method is responsible for parsing the ``iptables -Lxnv`` output
   for this match.  Notice the use of the ``-Lxnv`` options when
   implementing this method.

   This method should raise an :exc:`IptablesParsingError` if unable
   to parse the **iptables** output.

   This method may raise a :exc:`CriteriaExhaustedError` to terminate
   the match parsing process.

#. One or more methods returning instances of the match-specific criteria.
   In the example, the relevant method is :meth:`TcpmssMatch.mss()`
   (the :class:`TcpmssMatch` supports a single criterion)
   which returns an instance of the :class:`MssCriterion` class.

Finally, the new subclass **must** be registered with the :class:`MatchParser`
class by invoking the method :meth:`MatchParser.register_class`, and specifying
the keyword in the **iptables(8)** output that identifies the particular
match (in this example, that keyword is ``tcpmss``)


Adding a Criterion subclass
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A new :class:`Criterion` subclass **must** implement the following methods:

#. :meth:`equals`: this method expresses an equality comparison against
   a specific value. The method stores this value to be used later
   to generate the **iptables** arguments. In our example, the
   :class:`MssCriterion` comparison value is an integer or an integer
   range.

   Notice the invocation of :meth:`Match._set_polarity` at the end of this
   method; this is required and it serves two purposes:

   * it marks the criterion as having been **set**
   * it identifies that the criterion expresses an equality comparison
     (i.e. if the polarity were set to ``False``, the criterion would
     express an inequality comparison)

#. a method that returns the **iptables** arguments for implementing this
   criterion. In our example this method is
   :meth:`MssCriterion._crit_iptables_args`;
   it returns a list with the relevant **iptables** option and the stored
   value, e.g. ``['--mss', '500']``.
   This method is invoked by the :meth:`TcpmssMatch.to_iptables_args` method.


Supporting a new target
-----------------------

Supporting a new **iptables** target extension requires the addition of a new
:class:`Target` subclasss. This will be illustrated via example; the example
uses the implementation of the existing :class:`RejectTarget` class which
supports the **iptables** **REJECT** target extension.

All classes needed for implementing a new target are available in
the **linux.iptables.extension** module.

.. literalinclude:: target-example.py
    :language: python
    :linenos:


A new :class:`Target` subclass **must** implement the following methods:

#. :meth:`to_iptables_args`: this method should return the **iptables(8)**
   arguments for the target. In our example, the return value might look
   like this::

      ['-j', 'REJECT', '--reject-with', 'icmp-port-unreachable']
  
   assuming the :class:`RejectTarget` object was initialized with
   the particular ICMP message.

#. :meth:`parse`: this is a classmethod that takes a single argument of type
   :class:`TargetParser` and returns an instance of the new subclass.

   This method should raise an :exc:`IptablesParsingError` if unable
   to parse the **iptables** output.

The new subclass **must** be registered with the
:class:`TargetParser` class by invoking the method
:meth:`TargetParser.register_target`, and specifying
the target name.

If there is a field in the **iptables** output
that identifies the beginning of the target options, this field
can be passed as an argument to the :meth:`register_target` method.
In our example, this was the ``reject-with`` field.
Specifying such a field is optional. If specified, it
allows the field iterator inside the
:class:`TargetParser` instance, which is passed as an argument to the
:meth:`parse` method, to be positioned right after that field
(the iterator is accessible via the
:meth:`TargetParser.get_field_iterator` method).
Check the documentation of :meth:`TargetParser.register_target`
for possible arguments to this method.


-------


Base classes
------------

Match
~~~~~

The :class:`Match` class is the parent class of all match-related classes.

.. autoclass:: Match
    :members:
    :member-order: bysource


Criterion
~~~~~~~~~

The :class:`Criterion` class is the parent class of all classes implementing
match-specific criteria.
Objects of subclasses of :class:`Criterion` are never directly instantiated
by the user; they are instantiated
as needed by the :class:`Match` subclasses.

.. autoclass:: Criterion
    :members:
    :member-order: bysource
    :private-members: to_iptables_args, _crit_iptables_args


Target
~~~~~~

.. autoclass:: Target
    :members:
    :member-order: bysource

-------

Parser classes
--------------

MatchParser
~~~~~~~~~~~

A :class:`MatchParser` instance is used to parse the match part of
a rule in the **iptables(8)** output.

.. autoclass:: MatchParser
    :members:
    :member-order: bysource


LookaheadIterator
~~~~~~~~~~~~~~~~~

.. autoclass:: LookaheadIterator
    :members:
    :inherited-members:
    :member-order: bysource


TargetParser
~~~~~~~~~~~~

A :class:`TargetParser` instance is used to parse the target part of
a rule in the **iptables(8)** output.

.. autoclass:: TargetParser
    :members:
    :member-order: bysource


RuleFieldIterator
~~~~~~~~~~~~~~~~~

.. autoclass:: RuleFieldIterator
    :members:
    :inherited-members:
    :member-order: bysource
    :show-inheritance:

-------

Utility classes
---------------

BooleanCriterion
~~~~~~~~~~~~~~~~

.. autoclass:: BooleanCriterion
    :members:
    :member-order: bysource
    :show-inheritance:


GenericCriterion
~~~~~~~~~~~~~~~~

.. autoclass:: GenericCriterion
    :members:
    :member-order: bysource
    :show-inheritance:


GenericPositiveCriterion
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: GenericPositiveCriterion
    :members:
    :member-order: bysource
    :show-inheritance:
