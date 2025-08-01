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
This module provides the MasqueradeTarget class which provides access to
the iptables MASQUERADE target.
"""

from typing import List, Optional, Tuple

from ..deps import get_logger
from ..exceptions import IptablesParsingError

from .target import Target, TargetParser

_logger = get_logger("linuxnet.iptables.target.masqueradetarget")


class MasqueradeTarget(Target):
    """This class provides access to the ``MASQUERADE`` target
    """
    def __init__(self, *,
                port: Optional[int] =None, last_port: Optional[int] =None,
                is_random=False, is_random_fully=False):
        """
        :param port: port number (integer)
        :param last_port: port number (integer) used when defining
            a port range
        :param is_random: if ``True``, use the **iptables(8)**
            ``--random`` option
        :param is_random_fully: if ``True``, use the **iptables(8)**
            ``--random-fully`` option
        """
        super().__init__('MASQUERADE', terminates=True)
        self.__port = port
        self.__last_port = last_port
        self.__is_random = is_random
        self.__is_random_fully = is_random_fully

    def to_iptables_args(self) -> List[str]:
        """Returns a list of **iptables(8)** arguments
        """
        retval = super().to_iptables_args()
        if self.__port is not None:
            dest_spec = f':{self.__port:d}'
            if self.__last_port is not None:
                dest_spec += f'-{self.__last_port:d}'
            retval += ['--to-ports', dest_spec]
        if self.__is_random:
            retval.append('--random')
        if self.__is_random_fully:
            retval.append('--random-fully')
        return retval

    def uses_random_port_mapping(self) -> bool:
        """Returns the random target attribute
        """
        return self.__is_random

    def uses_fully_random_port_mapping(self) -> bool:
        """Returns the random-fully target attribute
        """
        return self.__is_random_fully

    def get_ports(self) -> Tuple[int, Optional[int]]:
        """Returns the port range
        """
        return (self.__port, self.__last_port)

    @classmethod
    def parse(cls, parser: TargetParser) -> Target:
        """Parse the ``MASQUERADE`` target options

        :meta private:
        """
        field_iter = parser.get_field_iter()
        # If there are arguments to the target, they are after the
        # field 'masq'/'random'/'random-fully' fields which are optional.
        field = field_iter.forward_to(['masq', 'random', 'random-fully'])
        if field is None:
            return MasqueradeTarget()
        port = None
        last_port = None
        is_random = False
        is_random_fully = False
        field_iter.put_back(field)
        for val in field_iter:
            try:
                if val == 'masq':
                    if next(field_iter) != 'ports:':
                        raise IptablesParsingError(
                                        "'masq' not followed by 'ports:'")
                    port_spec = next(field_iter)
                    if '-' in port_spec:
                        port_str, last_port_str = port_spec.split('-', 1)
                        port = int(port_str)
                        last_port = int(last_port_str)
                    else:
                        port = int(port_spec)
                elif val == 'random':
                    is_random = True
                elif val == 'random-fully':
                    is_random_fully = True
                else:
                    raise IptablesParsingError(
                        f'unknown MASQUERADE argument: {val}')
            except IptablesParsingError:
                raise
            except Exception as ex:
                raise IptablesParsingError(f'bad value for {val}') from ex
        return MasqueradeTarget(port=port, last_port=last_port,
                                        is_random=is_random,
                                        is_random_fully=is_random_fully)


TargetParser.register_target('MASQUERADE', MasqueradeTarget)
