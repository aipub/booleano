# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 by Gustavo Narea <http://gustavonarea.net/>.
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
Booleano operands.

"""


from booleano.nodes import OPERATIONS, OperationNode
from booleano.exc import InvalidOperationError, BadOperandError

__all__ = ("String", "Number", "Set", "Variable", "Function",
           "PlaceholderVariable", "PlaceholderFunction")


class _OperandMeta(type):
    """
    Metaclass for the operands.
    
    It checks that all the operands were defined correctly.
    
    """
    
    def __init__(cls, name, bases, ns):
        """
        Check the operations supported unless told otherwise.
        
        If the class defines the ``bypass_operation_check`` attribute and it
        evaluates to ``True``, :meth:`check_operations` won't be run.
        
        """
        type.__init__(cls, name, bases, ns)
        if not ns.get("bypass_operation_check"):
            cls.check_operations(name)
    
    def check_operations(cls, name):
        """
        Check that the operand supports all the relevant methods.
        
        :raises BadOperandError: If there are problems with the operations
            the operand claims to support.
        
        """
        if not cls.operations.issubset(OPERATIONS):
            raise BadOperandError("Operand %s supports unknown operations" %
                                  name)
        if len(cls.operations) == 0:
            raise BadOperandError("Operand %s must support at least one "
                                  "operation" % name)
        if not cls.is_implemented(cls.to_python):
            raise BadOperandError("Operand %s must define the .to_python() "
                                  "method" % name)
        # Checking the operations supported:
        if ("boolean" in cls.operations and 
            not cls.is_implemented(cls.__call__)):
            raise BadOperandError("Operand %s must return its truth value "
                                  "through .__call__() method" % name)
        if "equality" in cls.operations and not cls.is_implemented(cls.equals):
            raise BadOperandError("Operand %s must define the .equals() "
                                  "method because it supports equalities" %
                                  name)
        if ("inequality" in cls.operations and
            not (
                 cls.is_implemented(cls.less_than) and 
                 cls.is_implemented(cls.greater_than))
            ):
            raise BadOperandError("Operand %s must define the .greater_than() "
                                  "and .less_than() methods because it "
                                  "supports inequalities" % name)
        if ("membership" in cls.operations and
            not (
                 cls.is_implemented(cls.belongs_to) and 
                 cls.is_implemented(cls.is_subset))
            ):
            raise BadOperandError("Operand %s must define the .belongs_to() "
                                  "and .is_subset() methods because it "
                                  "supports memberships" % name)
    
    def is_implemented(cls, method):
        """Check that ``method`` is implemented."""
        return getattr(method, "implemented", True)


class Operand(OperationNode):
    """
    Base class for operands.
    
    """
    
    __metaclass__ = _OperandMeta
    
    #: Whether it should be checked that the operand really supports the
    #: operations it claims to support.
    bypass_operation_check = True
    
    #: The set of operations supported by this operand.
    operations = set()
    
    def to_python(self, context):
        """
        Return the value of this operand as a Python value.
        
        :param context: The evaluation context.
        :type context: object
        :return: The operand, converted to an analogous Python object.
        :rtype: object
        
        """
        raise NotImplementedError
    to_python.implemented = False
    
    def check_operation(self, operation):
        """
        Check that this operand supports ``operation``.
        
        :param operation: The operation this operand must support.
        :type operation: basestring
        :raises InvalidOperationError: If this operand doesn't support
            ``operation``.
        
        """
        if operation in self.operations:
            return
        raise InvalidOperationError('Operand "%s" does not support operation '
                                    '"%s"' % (repr(self), operation))
    
    #{ Unary operations
    
    def __call__(self, context):
        """
        Return the truth value of the operand.
        
        This is the *boolean* operation.
        
        :param context: The evaluation context.
        :type context: object
        :return: The logical value of the operand.
        :rtype: bool
        
        """
        raise NotImplementedError
    __call__.implemented = False
    
    #{ Binary operations
    
    def equals(self, value, context):
        """
        Check if this operand equals ``value``.
        
        :param context: The evaluation context.
        :type context: object
        
        This is an *equality* operation.
        
        """
        raise NotImplementedError
    equals.implemented = False
    
    def greater_than(self, value, context):
        """
        Check if this operand is greater than ``value``.
        
        :param context: The evaluation context.
        :type context: object
        
        This is an *inequality* operation.
        
        """
        raise NotImplementedError
    greater_than.implemented = False
    
    def less_than(self, value, context):
        """
        Check if this operand is less than ``value``.
        
        :param context: The evaluation context.
        :type context: object
        
        This is an *inequality* operation.
        
        """
        raise NotImplementedError
    less_than.implemented = False
    
    def belongs_to(self, value, context):
        """
        Check if this operand contains ``value``.
        
        :param context: The evaluation context.
        :type context: object
        
        This is a *membership* operation.
        
        """
        raise NotImplementedError
    belongs_to.implemented = False
    
    def is_subset(self, value, context):
        """
        Check if ``value`` is a subset of this operand.
        
        :param context: The evaluation context.
        :type context: object
        
        This is a *membership* operation.
        
        """
        raise NotImplementedError
    is_subset.implemented = False
    
    #}


# Importing the built-in operands so they can be available from this namespace:
from booleano.nodes.operands.constants import String, Number, Set
from booleano.nodes.operands.classes import Variable, Function
from booleano.nodes.operands.placeholders import (PlaceholderVariable,
                                                       PlaceholderFunction)
