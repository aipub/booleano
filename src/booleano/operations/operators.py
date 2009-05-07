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
Built-in operators.

"""

from booleano.operations import OPERATIONS
from booleano.operations.operands import Variable
from booleano.exc import InvalidOperationError, BadCallError, BadFunctionError

__all__ = ["FunctionOperator", "IfOperator", "NotOperator", "AndOperator",
           "OrOperator", "EqualsOperator", "LessThanOperator",
           "GreaterThanOperator", "LessEqualOperator", "GreaterEqualOperator",
           "ContainsOperator", "SubsetOperator"]


class Operator(object):
    """
    Base class for operators.
    
    The operands to be used by the operator must be passed in the constructor.
    
    """
    
    def __call__(self, **helpers):
        """
        Evaluate the operation, by passing the ``helpers`` to the inner
        operands/operators.
        
        """
        raise NotImplementedError
    
    @classmethod
    def check_operation(cls, operand, operation):
        """
        Check that ``operand`` supports ``operation``.
        
        :param operand: The operand in question.
        :type operand: :class:`booleano.operations.operands.Operand`
        :param operation: The operation ``operand`` must support.
        :type operation: basestring
        :raises InvalidOperationError: If ``operand doesn't support
            ``operation``.
        
        """
        if operation in operand.operations:
            return
        raise InvalidOperationError('Operand "%s" does not support operation '
                                    '"%s"' % (repr(operand), operation))


class UnaryOperator(Operator):
    """
    Base class for unary operators.
    
    .. attribute:: required_operations = ()
    
        All the operations the operand must support.
    
    """
    
    def __init__(self, operand):
        """
        Check that ``operand`` supports all the required operations before
        storing it.
        
        :param operand: The operand handled by this operator.
        :type operand: :class:`booleano.operations.operands.Operand`
        
        """
        for operation in self.required_operations:
            self.check_operation(operand, operation)
        self.operand = operand


class BinaryOperator(Operator):
    """
    Base class for binary operators.
    
    In binary operations, the two operands are marked as "master" or "slave".
    The binary operator will make the *master operand* perform the requested
    operation using the Python value of the *slave operand*. This is found by
    the :meth:`organize_operands` method, which can be overridden.
    
    """
    
    def __init__(self, left_operand, right_operand):
        """
        Instantiate this operator, finding the master operand among
        ``left_operand`` and ``right_operand``.
        
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
        Find the master and slave operands among the ``left_operand`` and 
        ``right_operand`` operands.
        
        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.operations.operands.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.operations.operands.Operand`
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


class FunctionOperator(Operator):
    """
    Base class for user-defined, n-ary function operators.
    
    Subclasses must override :meth:`check_arguments` to verify the validity of
    the arguments, or to do nothing if it's not necessary.
    
    .. attribute:: required_arguments = ()
    
        The names of the required arguments.
        
        For example, if you have a binary function whose required arguments
        are ``"name"`` and ``"address"``, your function should be defined as::
        
            class MyFunction(FunctionOperator):
                
                required_arguments = ("name", "address")
                
                # (...)
    
    .. attribute:: optional_arguments = {}
    
        The optional arguments along with their default values.
        
        This is a dictionary whose keys are the argument names and the items
        are their respective default values.
        
        For example, if you have a binary function whose arguments are both
        optional (``"name"`` and ``"address"``), your function should be 
        defined as::
        
            class MyFunction(FunctionOperator):
                
                # (...)
                
                optional_arguments = {
                    'name': "Gustavo",
                    'address': "Somewhere in Madrid",
                    }
                
                # (...)
        
        Then when it's called without these arguments, their default values
        will be taken.
    
    .. attribute:: arguments
    
        This is an instance attribute which represents the dictionary for the
        received arguments and their values (or their default values, for those
        optional arguments not set explicitly).
    
    .. attribute:: arity
    
        The arity of the function (i.e., the sum of the amount of the required
        arguments and the amount of optional arguments)
    
    .. attribute:: all_args
    
        The names of all the arguments, required and optional.
    
    """
    
    class __metaclass__(type):
        """
        Pre-process user-defined functions right after they've been defined.
        
        """
        
        def __init__(cls, name, bases, ns):
            """
            Calculate the arity of the function and create an utility variable
            which will contain all the valid arguments.
            
            """
            # A few short-cuts:
            req_args = ns.get("required_arguments", cls.required_arguments)
            opt_args = ns.get("optional_arguments", cls.optional_arguments)
            rargs_set = set(req_args)
            oargs_set = set(opt_args.keys())
            # Checking that are no duplicate entries:
            if len(rargs_set) != len(req_args) or rargs_set & oargs_set:
                raise BadFunctionError('Function "%s" has duplicate arguments'
                                       % name)
            # Merging all the arguments into a single list for convenience:
            cls.all_args = tuple(rargs_set | oargs_set)
            # Finding the arity:
            cls.arity = len(cls.all_args)
    
    required_arguments = ()
    
    optional_arguments = {}
    
    def __init__(self, *arguments):
        """
        Store the ``arguments`` and validate them.
        
        :raises BadCallError: If :meth:`check_arguments` finds that the
            ``arguments`` are invalid, or if few arguments are passed, or
            if too much arguments are passed.
        
        """
        # Checking the amount of arguments received:
        argn = len(arguments)
        if argn < len(self.required_arguments):
            raise BadCallError("Too few arguments")
        if argn > self.arity:
            raise BadCallError("Too many arguments")
        # Storing their values:
        self.arguments = self.optional_arguments.copy()
        for arg_pos in range(len(arguments)):
            arg_name = self.all_args[arg_pos]
            self.arguments[arg_name] = arguments[arg_pos]
        # Finally, check that all the parameters are correct:
        self.check_arguments()
    
    def check_arguments(self):
        """
        Check if all the arguments are correct.
        
        **This method must be overridden in subclasses**.
        
        The arguments dictionary will be available in the :attr:`arguments`
        attribute. If any of them is wrong, this method must raise a
        :class:`BadCallError` exception.
        
        :raises BadCallError: If at least one of the arguments are incorrect.
        
        """
        raise NotImplementedError


#{ Unary operators


class IfOperator(UnaryOperator):
    """
    Check if a *boolean operand* evaluates to ``True``.
    
    This is just a wrapper around the ``is_met`` method of the operand, useful
    for other operators to check the validity of one operand.
    
    """
    
    required_operations = ("boolean", )
    
    def __call__(self, **helpers):
        return self.operand.is_met(**helpers)


class NotOperator(IfOperator):
    """
    Check if a *boolean operand* evaluates to ``False``.
    
    """
    
    def __call__(self, **helpers):
        return not super(NotOperator, self).__call__(**helpers)


#{ Binary operators


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
