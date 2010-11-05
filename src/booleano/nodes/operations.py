# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://booleano.efous.org/>.
#
# This program is Freedomware: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
"""
Built-in operations.
    
.. note:: **Membership operations aren't supported on strings**

    Although both sets and strings are item collections, the former is 
    unordered and the later is ordered. If they were supported, there would
    some ambiguities to sort out, because users would expect the following
    operation results:
    
    - ``"ao" ⊂ "hola"`` is false: If strings were also sets, then the 
      resulting operation would be ``{"a", "o"} ⊂ {"h", "o", "l", "a"}``,
      which is true.
    - ``"la" ∈ "hola"`` is true: If strings were also sets, then the 
      resulting operation would be ``{"l", "a"} ∈ {"h", "o", "l", "a"}``, 
      which would be an *invalid operation* because the first operand must 
      be an item, not a set. But if we make an exception and take the first 
      operand as an item, the resulting operation would be 
      ``"la" ∈ {"h", "o", "l", "a"}``, which is not true.
    
    The solution to the problems above would involve some magic which
    contradicts the definition of a set: Take the second operand as an 
    *ordered collection*. But it'd just cause more trouble, because both
    operations would be equivalent!
    
    Also, there would be other issues to take into account (or not), like
    case-sensitivity.
    
    Therefore, if this functionality is needed, developers should create
    functions to handle it.

"""

from booleano.nodes import Function
from booleano.nodes.datatypes import Datatype, BooleanType, NumberType, SetType


__all__ = ["Not", "And", "Or", "Xor", "Equal", "NotEqual", "LessThan",
           "GreaterThan", "LessEqual", "GreaterEqual", "BelongsTo", "IsSubset"]


#{ Unary operators


class Not(Function, BooleanType):
    """
    The logical negation (``~``).
    
    Negate the boolean representation of an operand.
    
    """
    
    required_arguments = ("operand", )
    
    argument_types = BooleanType
    
    def get_as_boolean(self, context):
        return not self.arguments['operand'].get_as_boolean(context)


#{ Binary operators


class BinaryOperation(Function, BooleanType):
    """
    Base class for binary logical operators.
    
    """
    
    required_arguments = ("left_operand", "right_operand")


class _BinaryConnectiveOperation(BinaryOperation):
    """
    Base class for binary logic connectives.
    
    """
    
    is_commutative = True
    
    argument_types = BooleanType


class And(_BinaryConnectiveOperation):
    """
    The logical conjunction (``AND``).
    
    Connective that checks if two operations evaluate to ``True``.
    
    With this binary operator, the operands can be actual operands or
    operations.
    
    """
    
    def get_as_boolean(self, context):
        conjunction = (self.arguments['left_operand'].get_as_boolean(context)
                       and
                       self.arguments['right_operand'].get_as_boolean(context))
        
        return conjunction


class Or(_BinaryConnectiveOperation):
    """
    The logical inclusive disjunction (``OR``).
    
    Connective that check if at least one, out of two operations, evaluate to
    ``True``.
    
    With this binary operator, the operands can be actual operands or
    operations.
    
    """
    
    def get_as_boolean(self, context):
        disjunction = (self.arguments['left_operand'].get_as_boolean(context)
                       or
                       self.arguments['right_operand'].get_as_boolean(context))
        
        return disjunction


class Xor(_BinaryConnectiveOperation):
    """
    The logical exclusive disjunction (``XOR``).
    
    Connective that checks if only one, out of two operations, evaluate to
    ``True``.
    
    With this binary operator, the operands can be actual operands or
    operations.
    
    """
    
    def get_as_boolean(self, context):
        ex_disjunction = (self.arguments['left_operand'].get_as_boolean(context)
            ^
            self.arguments['right_operand'].get_as_boolean(context))
        
        return ex_disjunction


class Equal(BinaryOperation):
    """
    The equality operator (``==``).
    
    Checks that two operands are equivalent.
    
    For example: ``3 == 3``.
    
    """
    
    is_commutative = True
    
    argument_types = Datatype
    
    def get_as_boolean(self, context):
        # TODO: Requires the common datatype
        pass


# (x <> y) <=> ~(x == y)
class NotEqual(Equal):
    """
    The "not equal to" operator (``!=``).
    
    Checks that two operands are not equivalent.
    
    For example: ``3 != 2``.
    
    """
    
    def get_as_boolean(self, context):
        equals = super(NotEqual, self).get_as_boolean(context)
        return not equals


class _InequalityOperation(BinaryOperation):
    """
    Base class for inequalities.
    
    """
    
    argument_types = NumberType


class LessThan(_InequalityOperation):
    """
    The "less than" operator (``<``).
    
    For example: ``2 < 3``.
    
    """
    
    def get_as_boolean(self, context):
        left_operand = self.arguments['left_operand'].get_as_number(context)
        right_operand = self.arguments['right_operand'].get_as_number(context)
        
        return left_operand < right_operand


class GreaterThan(_InequalityOperation):
    """
    The "greater than" operator (``>``).
    
    For example: ``3 > 2``.
    
    """
    
    def get_as_boolean(self, context):
        left_operand = self.arguments['left_operand'].get_as_number(context)
        right_operand = self.arguments['right_operand'].get_as_number(context)
        
        return left_operand > right_operand


# (x <= y) <=> ~(x > y)
class LessEqual(GreaterThan):
    """
    The "less than or equal to" operator (``<=``).
    
    For example: ``2 <= 3``.
    
    """
    
    def get_as_boolean(self, context):
        return not super(LessEqual, self).get_as_boolean(context)


# (x >= y) <=> ~(x < y)
class GreaterEqual(LessThan):
    """
    The "greater than or equal to" operator (``>=``).
    
    For example: ``2 >= 2``.
    
    """
    
    def get_as_boolean(self, context):
        return not super(GreaterEqual, self).get_as_boolean(context)


class BelongsTo(BinaryOperation):
    """
    The "belongs to" operator (``∈``).
    
    For example: ``"valencia" ∈ {"caracas", "maracay", "valencia"}``.
    
    """
    
    argument_types = {'left_operand': Datatype, 'right_operand': SetType}
    
    def get_as_boolean(self, context):
        value = self.slave_operand.to_python(context)
        return self.master_operand.belongs_to(value, context)


class IsSubset(BinaryOperation):
    """
    The "is a subset of" operator (``⊂``).
    
    For example: ``{"valencia", "aragua"} ⊂ {"caracas", "aragua", "valencia"}``.
    
    """
    
    argument_types = SetType
    
    def get_as_boolean(self, context):
        subset = self.arguments['left_operand'].get_as_set(context)
        superset = self.arguments['right_operand'].get_as_set(context)
        
        is_subset = subset.issubset(superset)
        return is_subset


#}
