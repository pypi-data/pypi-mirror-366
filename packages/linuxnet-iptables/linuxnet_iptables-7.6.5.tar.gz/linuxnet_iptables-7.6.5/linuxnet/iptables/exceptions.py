# Copyright (c) 2021, 2024, Panagiotis Tsirigotis

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

"""iptables-related exceptions
"""

class IptablesError(Exception):
    """Root exception for all exceptions raised by modules of this package
    """

class IptablesParsingError(IptablesError):
    """Exception raised when there is a failure  parsing the
    ``iptables -xnv`` output
    """
    def __init__(self, *args, **kwargs):
        """
        :param line: the iptables output line that triggered the exception
        """
        self.__line = kwargs.pop('line', None)
        super().__init__(*args, **kwargs)

    def set_line(self, line: str) -> None:
        """Identify the line where the parsing error happened.
        Once set, this cannot be changed.
        Note that it may be set via the constructor.
        """
        if self.__line is None:
            self.__line = line

    def __str__(self):
        if self.__line is not None:
            line = self.__line or '<EMPTYLINE>'
            return f"{super().__str__()} (LINE='{line}')"
        return super().__str__()


class IptablesExecutionError(IptablesError):
    """Exception raised when the execution of the **iptables(8)** command fails
    """
    def __init__(self, *args, **kwargs):
        """
        :param prog: program whose execution failed (should be either
            ``iptables`` or ``ip6tables``)
        """
        self.__program = kwargs.pop('program', None)
        super().__init__(*args, **kwargs)

    def set_program(self, program: str) -> None:
        """Identify the program whose execution failed.
        Once set, this cannot be changed.
        Note that it may be set via the constructor.
        """
        if self.__program is None:
            self.__program = program

    def __str__(self):
        if self.__program is not None:
            return f"{super().__str__()} (PROGRAM='{self.__program}')"
        return super().__str__()
