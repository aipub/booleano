# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://booleano.efous.org/>.
#
# This program respects your freedom: you can redistribute it and/or modify it
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
Boolean operation nodes and utilities.

In other words, this package contains the elements of the parse trees.

Once parsed, the binary expressions are turned into the relevant operation
using the classes provided by this package.

"""

from booleano.exc import InvalidOperationError


__all__ = (
    # Operands:
    "String", "Number", "Set", "Variable", "Function", "PlaceholderVariable",
    "PlaceholderFunction",
    # Operators:
    "Not", "And", "Or", "Xor", "Equal", "NotEqual", "LessThan", "GreaterThan",
    "LessEqual", "GreaterEqual", "BelongsTo", "IsSubset",
)


#: The known/supported operations.
OPERATIONS = set((
    "equality",           # ==, !=
    "inequality",         # >, <, >=, <=
    "boolean",            # Logical values
    "membership",         # Set operations (i.e., ∈ and ⊂)
))


class OperationNode(object):
    """
    Base class for the individual elements available in a boolean operation
    (i.e., operands and operations).
    
    It can also be seen as the base class for each node in the parse trees.
    
    """
    
    def __call__(self, context):
        """
        Evaluate the operation, by passing the ``context`` to the inner
        operands/operators.
        
        :param context: The evaluation context.
        :type context: object
        :return: The logical value of the operation node.
        :rtype: bool
        
        """
        raise NotImplementedError()
    
    def check_logical_support(self):
        """
        Make sure this node has and can return its logical value.
        
        :raises booleano.exc.InvalidOperationError: If the node is an
            **operand** which doesn't support boolean operations.
        
        All the operators have logical values.
        
        """
        if self.is_operand():
            self.check_operation("boolean")
    
    def is_leaf(self):
        """
        Check if this is a leaf node.
        
        :rtype: bool
        
        Leaf nodes are those that don't contain other nodes (operands or
        operators): :class:`String`, :class:`Number`, :class:`Variable` and
        :class:`PlaceholderVariable`.
        
        """
        if (self.is_operator() or self.__class__ in (Set, PlaceholderFunction)
            or isinstance(self, Function)):
            return False
        return True
    
    def is_branch(self):
        """
        Check if this is a branch node.
        
        :rtype: bool
        
        Branch nodes are those that contain other nodes (operands or operators):
        All the operators, plus :class:`Set`, :class:`Function` and
        :class:`PlaceholderFunction`.
        
        """
        return not self.is_leaf()
    
    def is_operand(self):
        """
        Check if this node is an operand.
        
        :rtype: bool
        
        """
        return isinstance(self, Operand)
    
    def is_operator(self):
        """
        Check if this node is an operation.
        
        :rtype: bool
        
        """
        return isinstance(self, Operator)
    
    def check_equivalence(self, node):
        """
        Make sure ``node`` and this node are equivalent.
        
        :param node: The other node which may be equivalent to this one.
        :type node: :class:`OperationNode`
        :raises AssertionError: If both nodes have different classes.
        
        Operands and operations must extend this method to check for other
        attributes specific to such nodes.
        
        """
        error_msg = 'Nodes "%s" and "%s" are not equivalent'
        assert isinstance(node, self.__class__), error_msg % (repr(node),
                                                              repr(self))
    
    def __nonzero__(self):
        """
        Cancel the pythonic truth evaluation by raising an exception.
        
        :raises InvalidOperationError: To cancel the pythonic truth evaluation.
        
        This is disabled in order to prevent users from mistakenly assuming 
        they can evaluate operation nodes à la Python, which could lead to
        serious problems because they'd always evaluate to ``True``.
        
        Operation nodes must be evaluated passing the context explicitly.
        
        """
        raise InvalidOperationError("Operation nodes do not support Pythonic "
                                    "truth evaluation")
    
    def __eq__(self, other):
        """
        Check if the ``other`` node is equivalent to this one.
        
        :return: Whether they are equivalent.
        :rtype: bool
        
        """
        try:
            self.check_equivalence(other)
            return True
        except AssertionError:
            return False
    
    def __ne__(self, other):
        """
        Check if the ``other`` node is not equivalent to this one.
        
        :return: Whether they are not equivalent.
        :rtype: bool
        
        """
        try:
            self.check_equivalence(other)
            return False
        except AssertionError:
            return True
    
    def __str__(self):
        """
        Return the ASCII representation of this node.
        
        :raises NotImplementedError: If the Unicode representation is not
            yet implemented.
        
        If it contains non-English characters, they'll get converted into ASCII
        into ugly things -- It's best to use the Unicode representation
        directly.
        
        """
        as_unicode = self.__unicode__()
        return str(as_unicode.encode("utf-8"))
    
    def __unicode__(self):
        """
        Return the Unicode representation for this node.
        
        :raises NotImplementedError: If the Unicode representation is not
            yet implemented.
        
        """
        raise NotImplementedError("Node %s doesn't have an Unicode "
                                  "representation" % type(self))
    
    def __repr__(self):
        """
        Raise a NotImplementedError to force descendants to set the 
        representation explicitly.
        
        """
        raise NotImplementedError("Node %s doesn't have an "
                                  "representation" % type(self))


# Importing the built-in operands and operators so they can be available from
# this namespace:
from booleano.operations.operands import (String, Number, Set, Variable,
    Function, PlaceholderVariable, PlaceholderFunction, Operand)
from booleano.operations.operators import (Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset,
    Operator)
