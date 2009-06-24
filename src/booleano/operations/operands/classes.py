# -*- coding: utf-8 -*-
#
# Copyright (c) 2009 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.
"""
Booleano classes.

There are two types of Booleano classes:
 - Variable.
 - Function.

**Python classes and Booleano classes are two different things!**

"""
from booleano.operations.operands import Operand, _OperandMeta
from booleano.exc import BadOperandError, BadCallError, BadFunctionError

__all__ = ["Variable", "Function"]


class Class(Operand):
    """
    Base class for Booleano classes.
    
    """
    
    # Only actual classes should be checked.
    bypass_operation_check = True
    
    def to_string(self, global_name=None, namespace=None):
        raise NotImplementedError()
    
    def to_repr(self, global_name=None, names={}, namespace=None):
        raise NotImplementedError()
    
    def __unicode__(self):
        """Return the Unicode representation of this class."""
        return self.to_string()
    
    def __repr__(self):
        """Represent this class, including its translations."""
        return self.to_repr()


class Variable(Class):
    """
    Developer-defined variable.
    
    """
    
    # Only actual variables should be checked.
    bypass_operation_check = True
    
    def to_string(self, global_name=None, namespace=None):
        """Return the Unicode representation of this variable."""
        if not global_name:
            return "Unbound variable %s" % self.__class__.__name__
        name = global_name
        if namespace:
            namespace = u":".join(namespace)
            name = name + " (in %s)" % namespace
        return u"Variable %s" % name
    
    def to_repr(self, global_name=None, names={}, namespace=None):
        """Represent this variable, including its translations."""
        if not global_name:
            return "<Unbound variable %s at %s>" % (self.__class__.__name__,
                                                    id(self))
        names = ['%s="%s"' % (locale, name.encode("utf-8")) for (locale, name)
                 in names.items()]
        names.insert(0, self.global_name.encode("utf-8"))
        names = " ".join(names)
        if namespace:
            names = names + " (in %s)" % namespace
        return "<Variable %s>" % names


class _FunctionMeta(_OperandMeta):
    """
    Pre-process user-defined functions right after they've been defined.
    
    """
    
    def __init__(cls, name, bases, ns):
        """
        Calculate the arity of the function and create an utility variable
        which will contain all the valid arguments.
        
        Also checks that there are no duplicate arguments and that each argument
        is an operand.
        
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
        # Checking that the default values for the optional arguments are all
        # operands:
        for (key, value) in opt_args.items():
            if not isinstance(value, Operand):
                raise BadFunctionError('Default value for argument "%s" in '
                                       'function %s is not an operand' %
                                       (key, name))
        # Merging all the arguments into a single list for convenience:
        cls.all_args = tuple(rargs_set | oargs_set)
        # Finding the arity:
        cls.arity = len(cls.all_args)
        # Calling the parent constructor:
        super(_FunctionMeta, cls).__init__(name, bases, ns)


class Function(Class):
    """
    Base class for developer-defined, n-ary functions.
    
    A Booleano function is a `factory object
    <http://en.wikipedia.org/wiki/Factory_object>`_ because it always returns
    a Booleano operand.
    
    Subclasses must override :meth:`check_arguments` to verify the validity of
    the arguments, or to do nothing if it's not necessary.
    
    .. attribute:: required_arguments = ()
    
        The names of the required arguments.
        
        For example, if you have a binary function whose required arguments
        are ``"name"`` and ``"address"``, your function should be defined as::
        
            class MyFunction(Function):
                
                required_arguments = ("name", "address")
                
                # (...)
    
    .. attribute:: optional_arguments = {}
    
        The optional arguments along with their default values.
        
        This is a dictionary whose keys are the argument names and the items
        are their respective default values.
        
        For example, if you have a binary function whose arguments are both
        optional (``"name"`` and ``"address"``), your function should be 
        defined as::
        
            class MyFunction(Function):
                
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
    
    __metaclass__ = _FunctionMeta
    
    # Only actual functions should be checked.
    bypass_operation_check = True
    
    required_arguments = ()
    
    optional_arguments = {}
    
    def __init__(self, *arguments):
        """
        Store the ``arguments`` and validate them.
        
        :raises BadCallError: If :meth:`check_arguments` finds that the
            ``arguments`` are invalid, or if few arguments are passed, or
            if too much arguments are passed.
        
        """
        super(Function, self).__init__()
        # Checking the amount of arguments received:
        argn = len(arguments)
        if argn < len(self.required_arguments):
            raise BadCallError("Too few arguments")
        if argn > self.arity:
            raise BadCallError("Too many arguments")
        # Checking that all the arguments are operands:
        for argument in arguments:
            if not isinstance(argument, Operand):
                raise BadCallError('Argument "%s" is not an operand' %
                                   argument)
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
        
        :raises BadCallError: If at least one of the arguments are incorrect.
        
        **This method must be overridden in subclasses**.
        
        The arguments dictionary will be available in the :attr:`arguments`
        attribute. If any of them is wrong, this method must raise a
        :class:`BadCallError` exception.
        
        """
        raise NotImplementedError("Functions must validate the arguments")
    
    def check_equivalence(self, node):
        """
        Make sure function ``node`` and this function are equivalent.
        
        :param node: The other function which may be equivalent to this one.
        :type node: Function
        :raises AssertionError: If ``node`` is not a function or if it's a
            function but doesn't have the same arguments as this one OR doesn't
            have the same names as this one.
        
        """
        super(Function, self).check_equivalence(node)
        assert node.arguments == self.arguments, \
               "Functions %s and %s were called with different arguments" % \
               (node, self)
    
    def to_string(self, global_name=None, namespace=None):
        """Return the Unicode representation of this function."""
        args = [u'%s=%s' % (k, v) for (k, v) in self.arguments.items()]
        args = ", ".join(args)
        
        if not global_name:
            return "Unbound function %s(%s)" % (self.__class__.__name__, args)
        
        name = global_name
        if namespace:
            namespace = u":".join(namespace)
            name = name + " (in %s)" % namespace
        return u"Function %s" % name
    
    def to_repr(self, global_name=None, names={}, namespace=None):
        """
        Represent this function, including its translations.
        
        """
        args = ['%s=%s' % (k, repr(v)) for (k, v) in self.arguments.items()]
        args = ", ".join(args)
        
        if not global_name:
            return "<Unbound function %s(%s) at %s>" % (self.__class__.__name__,
                                                        args, id(self))
        
        names = ['%s="%s"' % (locale, name.encode("utf-8")) for (locale, name)
                 in names.items()]
        names.insert(0, self.global_name.encode("utf-8"))
        names = " ".join(names)
        if namespace:
            names = names + " (in %s)" % namespace
        return "<Function %s>" % names
