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
Operands.

"""

from booleano.operations import OPERATIONS, ParseTreeNode
from booleano.exc import (InvalidOperationError, BadOperandError, BadCallError,
                          BadFunctionError)

__all__ = ["Variable", "Function", "String", "Number", "Set"]


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
            cls.check_operations(name, bases, ns)
    
    def check_operations(cls, name, bases, ns):
        """
        Check that the operand supports all the relevant methods.
        
        :raises BadOperandError: If theere are problems with the operations
            the operand claims to support.
        
        """
        if not cls.operations.issubset(OPERATIONS):
            raise BadOperandError("Operand %s supports invalid operations" %
                                  name)
        if len(cls.operations) == 0:
            raise BadOperandError("Operand %s must support at least one "
                                  "operation" % name)
        if not cls.is_implemented(cls.to_python):
            raise BadOperandError("Operand %s must define the .to_python() "
                                  "method" % name)
        # Checking the operations supported:
        if ("boolean" in cls.operations and 
            not cls.is_implemented(cls.get_logical_value)):
            raise BadOperandError("Operand %s must define the  "
                                  ".get_logical_value() method" % name)
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
                 cls.is_implemented(cls.contains) and 
                 cls.is_implemented(cls.is_subset))
            ):
            raise BadOperandError("Operand %s must define the .contains() "
                                  "and .is_subset() methods because it "
                                  "supports memberships" % name)
    
    def is_implemented(cls, method):
        """Check that ``method`` is implemented."""
        return getattr(method, "implemented", True)

class Operand(ParseTreeNode):
    """
    Base class for operands.
    
    .. attribute:: operations = set()
        The set of operations supported by this operand.
    
    .. attribute:: bypass_operation_check = True
        Whether it should be checked that the operand really supports the
        operations it claims to support.
    
    """
    
    __metaclass__ = _OperandMeta
    
    bypass_operation_check = True
    
    operations = set()
    
    required_helpers = ()
    
    def to_python(self, **helpers):
        """
        Return the value of this operand as a Python value.
        
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
    
    def get_logical_value(self, **helpers):
        """
        Return the truth value of the operand.
        
        This is a *boolean* operation.
        
        """
        raise NotImplementedError
    get_logical_value.implemented = False
    
    #{ Binary operations
    
    def equals(self, value, **helpers):
        """
        Check if this operand equals ``value``.
        
        This is an *equality* operation.
        
        """
        raise NotImplementedError
    equals.implemented = False
    
    def greater_than(self, value, **helpers):
        """
        Check if this operand is greater than ``value``.
        
        This is an *inequality* operation.
        
        """
        raise NotImplementedError
    greater_than.implemented = False
    
    def less_than(self, value, **helpers):
        """
        Check if this operand is less than ``value``.
        
        This is an *inequality* operation.
        
        """
        raise NotImplementedError
    less_than.implemented = False
    
    def contains(self, value, **helpers):
        """
        Check if this operand contains ``value``.
        
        This is a *membership* operation.
        
        """
        raise NotImplementedError
    contains.implemented = False
    
    def is_subset(self, value, **helpers):
        """
        Check if ``value`` is a subset of this operand.
        
        This is a *membership* operation.
        
        """
        raise NotImplementedError
    is_subset.implemented = False
    
    #}


class _VariableMeta(_OperandMeta):
    """Metaclass for the translatable nodes."""
    
    def __init__(cls, name, bases, ns):
        """Lower-case the default names for the node."""
        _OperandMeta.__init__(cls, name, bases, ns)
        if cls.default_global_name:
            cls.default_global_name = cls.default_global_name.lower()
        for (locale, name) in cls.default_names.items():
            cls.default_names[locale] = name.lower()


class Variable(Operand):
    """
    User-defined variable.
    
    """
    
    __metaclass__ = _VariableMeta
    
    # Only actual variables should be checked.
    bypass_operation_check = True
    
    default_global_name = None
    
    default_names = {}
    
    def __init__(self, global_name=None, **names):
        """
        Create the variable using ``global_name`` as it's default name.
        
        :param global_name: The global name used by this variable; if not set,
            the :attr:`default_global_name` will be used.
        :type global_name: basestring
        :raises BadOperandError: If the variable class doesn't set a default
            global name and ``global_name`` is not set either.
        
        Additional keyword arguments represent the other names this variable
        can take in different languages.
        
        .. note::
            ``global_name`` does *not* have to be an English/ASCII string.
        
        """
        if global_name:
            self.global_name = global_name.lower()
        elif self.default_global_name:
            self.global_name = self.default_global_name
        else:
            raise BadOperandError("%s doesn't have a default global name; set"
                                  "one explicitly" % self.__class__.__name__)
        self.names = self.default_names.copy()
        # Convert the ``names`` to lower-case, before updating the resulting
        # names:
        for (locale, name) in names.items():
            names[locale] = name.lower()
        self.names.update(names)
    
    def check_equivalence(self, node):
        """
        Make sure variable ``node`` and this variable are equivalent.
        
        :param node: The other variable which may be equivalent to this one.
        :type node: Variable
        :raises AssertionError: If the nodes don't share the same class or
            don't share the same global and localized names.
        
        """
        super(Variable, self).check_equivalence(node)
        assert node.global_name == self.global_name, \
               u'Translatable nodes %s and %s have different global names' % \
               (self, node)
        assert node.names == self.names, \
               u'Translatable nodes %s and %s have different translations' % \
               (self, node)
    
    def __unicode__(self):
        """Return the Unicode representation of this variable."""
        return "Variable %s" % self.global_name
    '''
    def __repr__(self):
        """Represent this variable, including its translations."""
        translations = ['%s="%s"' % (locale, name) for (locale, name)
                        in self.names]
        translations = " ".join(translations)
        return "<Variable %s %s>" % (self.global_name, translations)
    '''



class _FunctionMeta(_VariableMeta):
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


class Function(Variable):
    """
    Base class for user-defined, n-ary functions.
    
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
    
    def __init__(self, global_name=None, *arguments, **names):
        """
        Store the ``arguments`` and validate them.
        
        :param global_name: The global name for this function; if not set,
            the :attr:`default_global_name` will be used..
        :raises BadCallError: If :meth:`check_arguments` finds that the
            ``arguments`` are invalid, or if few arguments are passed, or
            if too much arguments are passed.
        :raises BadOperandError: If the function class doesn't set a default
            global name and ``global_name`` is not set either.
        
        Additional keyword arguments will be used to find the alternative names
        for this functions in various grammars.
        
        """
        super(Function, self).__init__(global_name, **names)
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
    
    def __unicode__(self):
        """Return the Unicode representation for this function."""
        args = [u'%s=%s' % (k, v) for (k, v) in self.arguments.items()]
        args = ", ".join(args)
        return "%s(%s)" % (self.global_name, args)


#{ Constants


class Constant(Operand):
    """
    Base class for constant operands.
    
    The only operation that is common to all the constants is equality (see
    :meth:`equals`).
    
    Constants don't rely on helpers -- they are constant!
    
    .. warning::
        This class is available as the base for the built-in :class:`String`,
        :class:`Number` and :class:`Set` classes. User-defined constants aren't
        supported; use :class:`Variable` instead.
    
    """
    
    operations = set(['equality'])
    
    def __init__(self, constant_value):
        """
        Initialize this constant as ``constant_value``.
        
        """
        self.constant_value = constant_value
    
    def to_python(self, **helpers):
        """
        Return the value represented by this constant.
        
        """
        return self.constant_value
    
    def equals(self, value, **helpers):
        """
        Check if this constant equals ``value``.
        
        """
        return self.constant_value == value
    
    def check_equivalence(self, node):
        """
        Make sure constant ``node`` and this constant are equivalent.
        
        :param node: The other constant which may be equivalent to this one.
        :type node: Constant
        :raises AssertionError: If the constants are of different types or
            represent different values.
        
        """
        super(Constant, self).check_equivalence(node)
        assert node.constant_value == self.constant_value, \
               u'Constants %s and %s represent different values' % (self,
                                                                    node)
    '''
    def __repr__(self):
        """Represent this constant."""
        return "<Constant %s>" % unicode(self)
    '''


class String(Constant):
    u"""
    Constant string.
    
    These constants only support equality operations.
    
    .. note:: **Membership operations aren't supported**
    
        Although both sets and strings are item collections, the former is 
        unordered and the later is ordered. If they were supported, there would
        some ambiguities to sort out, because users would expect the following
        operation results::
        
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
        function operators to handle it.
    
    """
    
    def __init__(self, string):
        """Turn ``string`` into a string if it isn't a string yet"""
        string = unicode(string)
        super(String, self).__init__(string)
    
    def equals(self, value, **helpers):
        """Turn ``value`` into a string if it isn't a string yet"""
        value = unicode(value)
        return super(String, self).equals(value, **helpers)
    
    def __unicode__(self):
        """Return the Unicode representation of this constant string."""
        return u'"%s"' % self.constant_value


class Number(Constant):
    """
    Float and integer constants.
    
    These constants support inequality operations; see :meth:`greater_than`
    and :meth:`less_than`.
    
    Internally, this number is treated like a float, even if it was an
    integer initially.
    
    """
    
    operations = Constant.operations | set(['inequality'])
    
    def __init__(self, number):
        """
        Turn ``number`` into a float before instantiating this constant.
        
        """
        number = float(number)
        super(Number, self).__init__(number)
    
    def equals(self, value, **helpers):
        """
        Check if this numeric constant equals ``value``.
        
        ``value`` will be turned into a float prior to the comparison, to 
        support strings.
        
        :raises InvalidOperationError: If ``value`` can't be turned into a
            float.
        
        """
        try:
            value = float(value)
        except ValueError:
            raise InvalidOperationError('"%s" is not a number' % value)
        
        return super(Number, self).equals(value, **helpers)
    
    def greater_than(self, value, **helpers):
        """
        Check if this numeric constant is greater than ``value``.
        
        ``value`` will be turned into a float prior to the comparison, to
        support strings.
        
        """
        return self.constant_value > float(value)
    
    def less_than(self, value, **helpers):
        """
        Check if this numeric constant is less than ``value``.
        
        ``value`` will be turned into a float prior to the comparison, to
        support strings.
        
        """
        return self.constant_value < float(value)
    
    def __unicode__(self):
        """Return the Unicode representation of this constant number."""
        return unicode(self.constant_value)


class Set(Constant):
    """
    Constant sets.
    
    These constants support membership operations; see :meth:`contains` and
    :meth:`is_subset`.
    
    """
    
    operations = Constant.operations | set(["inequality", "membership"])
    
    def __init__(self, *items):
        """
        Check that each item in ``items`` is an operand before setting up this
        set.
        
        :raises InvalidOperationError: If at least one of the ``items`` is not
            an instance of :class:`Operand`.
        
        """
        for item in items:
            if not isinstance(item, Operand):
                raise InvalidOperationError('Item "%s" is not an operand, so '
                                            'it cannot be a member of a set' %
                                            item)
        super(Set, self).__init__(set(items))
    
    def to_python(self, **helpers):
        """
        Return a set made up of the Python representation of the operands
        contained in this set.
        
        """
        items = set(item.to_python(**helpers) for item in self.constant_value)
        return items
    
    def equals(self, value, **helpers):
        """Check if all the items in ``value`` are the same of this set."""
        value = set(value)
        return value == self.to_python(**helpers)
    
    def less_than(self, value, **helpers):
        """
        Check if this set has less items than the number represented in 
        ``value``.
        
        :raises InvalidOperationError: If ``value`` is not an integer.
        
        """
        try:
            value = float(value)
            if not value.is_integer():
                raise ValueError
        except ValueError:
            raise InvalidOperationError('To compare the amount of items in a '
                                        'set, the operand "%s" has to be an '
                                        'integer')
        return len(self.constant_value) < value
    
    def greater_than(self, value, **helpers):
        """
        Check if this set has more items than the number represented in 
        ``value``.
        
        :raises InvalidOperationError: If ``value`` is not an integer.
        
        """
        try:
            value = float(value)
            if not value.is_integer():
                raise ValueError
        except ValueError:
            raise InvalidOperationError('To compare the amount of items in a '
                                        'set, the operand "%s" has to be an '
                                        'integer')
        return len(self.constant_value) > value
    
    def contains(self, value, **helpers):
        """
        Check that this constant set contains the ``value`` item.
        
        """
        for item in self.constant_value:
            try:
                if item.equals(value, **helpers):
                    return True
            except InvalidOperationError:
                continue
        return False
    
    def is_subset(self, value, **helpers):
        """
        Check that the ``value`` set is a subset of this constant set.
        
        """
        for item in value:
            if not self.contains(item, **helpers):
                return False
        return True
    
    def check_equivalence(self, node):
        """
        Make sure set ``node`` and this set are equivalent.
        
        :param node: The other set which may be equivalent to this one.
        :type node: Set
        :raises AssertionError: If ``node`` is not a set or it's a set 
            with different elements.
        
        """
        Operand.check_equivalence(self, node)
        
        unmatched_elements = list(self.constant_value)
        assert len(unmatched_elements) == len(node.constant_value), \
               u'Sets %s and %s do not have the same cardinality' % \
               (unmatched_elements, node)
        
        # Checking that each element is represented by a mock operand:
        for element in node.constant_value:
            for key in range(len(unmatched_elements)):
                if unmatched_elements[key] == element:
                    del unmatched_elements[key]
                    break
        
        assert 0 == len(unmatched_elements), \
               u'No match for the following elements: %s' % unmatched_elements
    
    def __unicode__(self):
        """Return the Unicode representation of this constant set."""
        elements = [unicode(element) for element in self.constant_value]
        elements = u", ".join(elements)
        return "{%s}" % elements


#}
