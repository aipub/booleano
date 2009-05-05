# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 by Gustavo Narea <http://gustavonarea.net/>
#
# This file is part of Conditions <http://code.gustavonarea.net/conditions/>
#
# Conditions is freedomware: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# Conditions is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Conditions. If not, see <http://www.gnu.org/licenses/>.
"""
Exceptions raised by :mod:`conditions`.

"""

__all__ = ['InvalidOperationError']


class ConditionsException(Exception):
    """
    Base class for the exceptions.
    
    """
    pass


#{ Operation-related errors


class InvalidOperationError(ConditionsException):
    """
    Exception raised when trying to apply an operation on an operand that
    doesn't support it.
    
    For example: ``"word" > 10``.
    
    """
    pass


#}
