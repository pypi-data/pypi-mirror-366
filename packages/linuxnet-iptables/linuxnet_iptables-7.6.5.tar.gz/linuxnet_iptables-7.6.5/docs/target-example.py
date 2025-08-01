# Copyright (c) 2021-2024, Panagiotis Tsirigotis

"""
Example module implementing a class to support the REJECT target
"""

from typing import List, Optional
from linuxnet.iptables.extension import Target, TargetParser

class RejectTarget(Target):
    """This class provides access to the ``REJECT`` target
    """
    def __init__(self, reject_with: Optional[str] =None):
        """
        :param reject_with: optional ``ICMP`` message type
        """
        super().__init__('REJECT', terminates=True)
        self.__reject_with = reject_with

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        retval = super().to_iptables_args()
        if self.__reject_with is not None:
            retval += ['--reject-with', self.__reject_with]
        return retval

    @classmethod
    def parse(cls, parser: TargetParser) -> Target:
        """Parse the REJECT target options
        """
        field_iter = parser.get_field_iter()
        icmp_message = field_iter.next_value('reject-with')
        return RejectTarget(reject_with=icmp_message)

TargetParser.register_target('REJECT', RejectTarget, 'reject-with')
