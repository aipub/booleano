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

from booleano.nodes import OperationNode

__all__ = ("Not", "And", "Or", "Xor", "Equal", "NotEqual", "LessThan",
           "GreaterThan", "LessEqual", "GreaterEqual", "BelongsTo", "IsSubset")


class Operation(OperationNode):
    """
    Base class for logical operations.
    
    The operands to be used by the operation must be passed in the constructor.
    
    """
    pass


class UnaryOperation(Operation):
    """
    Base class for unary logical operations.
    
    """
    
    def __init__(self, operand):
        """
        Check that ``operand`` supports all the required operations before
        storing it.
        
        :param operand: The operand handled by this operator.
        :type operand: :class:`booleano.nodes.constants.Operand`
        
        """
        self.operand = operand
    
    def check_equivalence(self, node):
        """
        Make sure unary operator ``node`` and this unary operator are
        equivalent.
        
        :param node: The other operator which may be equivalent to this one.
        :type node: UnaryOperation
        :raises AssertionError: If ``node`` is not a unary operator or if it's
            an unary operator but doesn't have the same operand as this one.
        
        """
        super(UnaryOperation, self).check_equivalence(node)
        assert node.operand == self.operand, \
               'Operands of unary operations %s and %s are not equivalent' % \
               (node, self)
    
    def __unicode__(self):
        """
        Return the Unicode representation for this operator and its operand.
        
        """
        operand = unicode(self.operand)
        return u"%s(%s)" % (self.__class__.__name__, operand)
    
    def __repr__(self):
        """Return the representation for this operator and its operand."""
        operand = repr(self.operand)
        return "<%s %s>" % (self.__class__.__name__, operand)


class BinaryOperation(Operation):
    """
    Base class for binary logical operators.
    
    In binary operations, the two operands are marked as "master" or "slave".
    The binary operator will make the *master operand* perform the requested
    operation using the Python value of the *slave operand*. This is found by
    the :meth:`organize_operands` method, which can be overridden.
    
    .. attribute:: master_operand
    
        The instance attribute that represents the master operand.
    
    .. attribute:: slave_operand
    
        The instance attribute that represents the slave operand.
    
    """
    
    def __init__(self, left_operand, right_operand):
        """
        Instantiate this operator, finding the master operand among
        ``left_operand`` and ``right_operand``.
        
        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.nodes.constants.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.nodes.constants.Operand`
        
        """
        master, slave = self.organize_operands(left_operand, right_operand)
        self.master_operand = master
        self.slave_operand = slave
    
    def organize_operands(self, left_operand, right_operand):
        """
        Find the master and slave operands among the ``left_operand`` and 
        ``right_operand`` operands.
        
        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.nodes.constants.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.nodes.constants.Operand`
        :return: A pair where the first item is the master operand and the
            second one is the slave.
        :rtype: tuple
        
        In practice, they are only distinguished when one of the operands is a
        variable and the other is a constant. In such situations, the variable
        becomes the master operand and the constant becomes the slave operand.
        
        When both operands are constant or both are variable, the left-hand 
        operand becomes the master and the right-hand operand becomes the slave.
        
        """
        l_var = isinstance(left_operand, Variable)
        r_var = isinstance(right_operand, Variable)
        
        if l_var == r_var or l_var:
            # Both operands are variable/constant, OR the left-hand operand is 
            # a variable and the right-hand operand is a constant.
            return (left_operand, right_operand)
        
        # The right-hand operand is the variable and the left-hand operand the
        # constant:
        return (right_operand, left_operand)
    
    def check_equivalence(self, node):
        """
        Make sure binary operator ``node`` and this binary operator are
        equivalent.
        
        :param node: The other operator which may be equivalent to this one.
        :type node: BinaryOperation
        :raises AssertionError: If ``node`` is not a binary operator or if it's
            an binary operator but doesn't have the same operands as this one.
        
        """
        super(BinaryOperation, self).check_equivalence(node)
        same_operands = (
            (node.master_operand == self.master_operand and
             node.slave_operand == self.slave_operand)
            or
            (node.master_operand == self.slave_operand and
             self.master_operand == node.slave_operand)
        )
        assert same_operands, \
               'Operands of binary operations %s and %s are not equivalent' % \
               (node, self)
    
    def __unicode__(self):
        """
        Return the Unicode representation for this binary operator, including
        its operands.
        
        """
        return u"%s(%s, %s)" % (self.__class__.__name__, self.master_operand,
                                self.slave_operand)
    
    def __repr__(self):
        """
        Return the representation for this binary operator, including its
        operands.
        
        """
        return "<%s %s %s>" % (self.__class__.__name__,
                               repr(self.master_operand),
                               repr(self.slave_operand))


#{ Unary operators


class Not(UnaryOperation):
    """
    The logical negation (``~``).
    
    Negate the boolean representation of an operand.
    
    """
    
    def __init__(self, operand):
        """
        
        :raises booleano.exc.InvalidOperationError: If ``operand`` doesn't have
            a logical value.
        
        """
        operand.check_logical_support()
        super(Not, self).__init__(operand)
    
    def __call__(self, context):
        """
        Return the negate of the truth value for the operand.
        
        :param context: The evaluation context.
        :type context: object
        
        """
        return not self.operand(context)


#{ Binary operators


class _ConnectiveOperation(BinaryOperation):
    """
    Logic connective to turn the left-hand and right-hand operands into
    boolean operations, so we can manipulate their truth value easily.
    
    """
    
    def __init__(self, left_operand, right_operand):
        """
        
        :raises booleano.exc.InvalidOperationError: If ``left_operand`` or 
            ``right_operand`` doesn't have logical values.
        
        """
        left_operand.check_logical_support()
        right_operand.check_logical_support()
        super(_ConnectiveOperation, self).__init__(left_operand, right_operand)


class And(_ConnectiveOperation):
    """
    The logical conjunction (``AND``).
    
    Connective that checks if two operations evaluate to ``True``.
    
    With this binary operator, the operands can be actual operands or
    operations.
    
    """
    
    def __call__(self, context):
        """
        Check if both operands evaluate to ``True``.
        
        :param context: The evaluation context.
        :type context: objects
        
        """
        return self.master_operand(context) and self.slave_operand(context)


class Or(_ConnectiveOperation):
    """
    The logical inclusive disjunction (``OR``).
    
    Connective that check if at least one, out of two operations, evaluate to
    ``True``.
    
    With this binary operator, the operands can be actual operands or
    operations.
    
    """
    
    def __call__(self, context):
        """
        Check if at least one of the operands evaluate to ``True``.
        
        :param context: The evaluation context.
        :type context: object
        
        """
        return self.master_operand(context) or self.slave_operand(context)


class Xor(_ConnectiveOperation):
    """
    The logical exclusive disjunction (``XOR``).
    
    Connective that checks if only one, out of two operations, evaluate to
    ``True``.
    
    With this binary operator, the operands can be actual operands or
    operations.
    
    """
    
    def __call__(self, context):
        """
        Check that only one of the operands evaluate to ``True``.
        
        :param context: The evaluation context.
        :type context: object
        
        """
        return self.master_operand(context) ^ self.slave_operand(context)


class Equal(BinaryOperation):
    """
    The equality operator (``==``).
    
    Checks that two operands are equivalent.
    
    For example: ``3 == 3``.
    
    """
    
    def __init__(self, left_operand, right_operand):
        """
        
        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.nodes.constants.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.nodes.constants.Operand`
        :raises booleano.exc.InvalidOperationError: If the master operand
            between ``left_operand`` or ``right_operand`` doesn't support
            equality operations.
        
        """
        super(Equal, self).__init__(left_operand, right_operand)
        self.master_operand.check_operation("equality")
    
    def __call__(self, context):
        value = self.slave_operand.to_python(context)
        return self.master_operand.equals(value, context)


# (x <> y) <=> ~(x == y)
class NotEqual(Equal):
    """
    The "not equal to" operator (``!=``).
    
    Checks that two operands are not equivalent.
    
    For example: ``3 != 2``.
    
    """
    
    def __call__(self, context):
        return not super(NotEqual, self).__call__(context)


class _InequalityOperation(BinaryOperation):
    """
    Handle inequalities (``<``, ``>``) and switch the operation if the operands
    are rearranged.
    
    """
    
    def __init__(self, left_operand, right_operand, comparison):
        """
        Switch the ``comparison`` if the operands are rearranged.
        
        :param left_operand: The original left-hand operand in the inequality.
        :param right_operand: The original right-hand operand in the
            inequality.
        :param comparison: The symbol for the particular inequality (i.e.,
            "<" or ">").
        :raises InvalidOperationError: If the master operand doesn't support
            inequalities.
        
        If the operands are rearranged by :meth:`organize_operands`, then
        the operation must be switched (e.g., from "<" to ">").
        
        This will also "compile" the comparison operation; otherwise, it'd have
        to be calculated on a per evaluation basis.
        
        """
        super(_InequalityOperation, self).__init__(left_operand, right_operand)
        
        self.master_operand.check_operation("inequality")
        
        if left_operand != self.master_operand:
            # The operands have been rearranged! Let's invert the comparison:
            if comparison == "<":
                comparison = ">"
            else:
                comparison = "<"
        
        # "Compiling" the comparison:
        if comparison == ">":
            self.comparison = self._greater_than
        else:
            self.comparison = self._less_than
    
    def __call__(self, context):
        return self.comparison(context)
    
    def _greater_than(self, context):
        """Check if the master operand is greater than the slave"""
        value = self.slave_operand.to_python(context)
        return self.master_operand.greater_than(value, context)
    
    def _less_than(self, context):
        """Check if the master operand is less than the slave"""
        value = self.slave_operand.to_python(context)
        return self.master_operand.less_than(value, context)


class LessThan(_InequalityOperation):
    """
    The "less than" operator (``<``).
    
    For example: ``2 < 3``.
    
    """
    
    def __init__(self, left_operand, right_operand):
        super(LessThan, self).__init__(left_operand, right_operand, "<")


class GreaterThan(_InequalityOperation):
    """
    The "greater than" operator (``>``).
    
    For example: ``3 > 2``.
    
    """
    
    def __init__(self, left_operand, right_operand):
        super(GreaterThan, self).__init__(left_operand, right_operand,
                                                  ">")


# (x <= y) <=> ~(x > y)
class LessEqual(GreaterThan):
    """
    The "less than or equal to" operator (``<=``).
    
    For example: ``2 <= 3``.
    
    """
    
    def __call__(self, context):
        return not super(LessEqual, self).__call__(context)


# (x >= y) <=> ~(x < y)
class GreaterEqual(LessThan):
    """
    The "greater than or equal to" operator (``>=``).
    
    For example: ``2 >= 2``.
    
    """
    
    def __call__(self, context):
        return not super(GreaterEqual, self).__call__(context)


class _SetOperation(BinaryOperation):
    """
    Base class for set-related operators.
    
    """
    
    def __init__(self, left_operand, right_operand):
        """
        
        :raises booleano.exc.InvalidOperationError: If ``right_operand``
            doesn't support membership operations.
        
        """
        super(_SetOperation, self).__init__(left_operand, right_operand)
        self.master_operand.check_operation("membership")
    
    def organize_operands(self, left_operand, right_operand):
        """Set the set (right-hand operand) as the master operand."""
        return (right_operand, left_operand)


class BelongsTo(_SetOperation):
    """
    The "belongs to" operator (``∈``).
    
    For example: ``"valencia" ∈ {"caracas", "maracay", "valencia"}``.
    
    """
    
    def __call__(self, context):
        value = self.slave_operand.to_python(context)
        return self.master_operand.belongs_to(value, context)


class IsSubset(_SetOperation):
    """
    The "is a subset of" operator (``⊂``).
    
    For example: ``{"valencia", "aragua"} ⊂ {"caracas", "aragua", "valencia"}``.
    
    """
    
    def __call__(self, context):
        value = self.slave_operand.to_python(context)
        return self.master_operand.is_subset(value, context)


#}
