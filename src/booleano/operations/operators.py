# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 by Gustavo Narea <http://gustavonarea.net/>
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>
#
# Booleano is freedomware: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# Booleano is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Booleano. If not, see <http://www.gnu.org/licenses/>.
"""
Operators.

"""

from booleano.operations import OPERATIONS
from booleano.exc import InvalidOperationError

__all__ = ["FunctionOperator", "IfOperator", "NotOperator", "AndOperator",
           "OrOperator", "EqualsOperator", "LessThanOperator",
           "GreaterThanOperator", "LessEqualOperator", "GreaterEqualOperator",
           "ContainsOperator", "SubsetOperator"]


class Operator(object):
    """
    Base class for operators.
    
    """
    
    def __call__(self, **helpers):
        raise NotImplementedError


class UnaryOperator(Operator):
    """
    Base class for unary operators.
    
    """
    
    def __init__(self, operand):
        """
        
        :param operand: The operand handled by this operator.
        :type operand: :class:`booleano.operations.operands.Operand`
        
        """
        self.operand = operand


class BinaryOperator(Operator):
    """
    Base class for binary operators.
    
    In binary operations, the two operands are marked as "master" and "slave".
    The binary operator will make the *master operand* perform the requested
    operation using the Python value of the *slave operand*.
    
    In practice, they are only distinguished when one of the operands is a
    variable and the other is a constant. In such situations, the variable
    becomes the master operand and the constant becomes the slave operand.
    
    When both operands are
    
    """
    
    def __init__(self, left_operand, right_operand):
        """
        
        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.operations.operands.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.operations.operands.Operand`
        
        """
        master, slave = self.organize_operands(left_operand, right_operand)
        self.master_operand = master
        self.slave_operand = slave
    
    def organize_operands(self, left_operand, right_operand):
        """
        Find the master and slave operands in the ``left_operand`` and 
        ``right_operand``.
        
        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.operations.operands.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.operations.operands.Operand`
        
        """
        raise NotImplementedError


class FunctionOperator(Operator):
    """
    Base class for user-defined, n-ary function operators.
    
    """
    arity = None


class IfOperator(UnaryOperator):
    pass

class NotOperator(UnaryOperator):
    def __call__(self, **helpers):
        return not super(NotOperator, self).__call__(**helpers)

class AndOperator(BinaryOperator):
    pass

class OrOperator(BinaryOperator):
    pass

class EqualsOperator(BinaryOperator):
    pass

class LessThanOperator(BinaryOperator):
    pass

class GreaterThanOperator(BinaryOperator):
    pass

class LessEqualOperator(BinaryOperator):
    pass

class GreaterEqualOperator(BinaryOperator):
    pass

class ContainsOperator(BinaryOperator):
    pass

class SubsetOperator(BinaryOperator):
    pass


#}
