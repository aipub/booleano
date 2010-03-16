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


#{ Built-in operands


class Constant(Operand):
    """
    Base class for constant operands.
    
    The only operation that is common to all the constants is equality (see
    :meth:`equals`).
    
    Constants don't rely on the context -- they are constant!
    
    .. warning::
        This class is available as the base for the built-in :class:`String`,
        :class:`Number` and :class:`Set` classes. User-defined constants aren't
        supported, but you can assign a name to a constant (see
        :term:`binding`).
    
    """
    
    operations = set(['equality'])
    
    def __init__(self, constant_value):
        """
        
        :param constant_value: The Python value represented by the Booleano
            constant.
        :type constant_value: :class:`object`
        
        """
        self.constant_value = constant_value
    
    def to_python(self, context):
        """
        Return the value represented by this constant.
        
        """
        return self.constant_value
    
    def equals(self, value, context):
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


class String(Constant):
    u"""
    Constant string.
    
    These constants only support equality operations.
    
    .. note:: **Membership operations aren't supported**
    
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
    
    def __init__(self, string):
        """
        
        :param string: The Python string to be represented by this Booleano
            string.
        :type string: :class:`basestring`
        
        ``string`` will be converted to :class:`unicode`, so it doesn't
        have to be a :class:`basestring` initially.
        
        """
        string = unicode(string)
        super(String, self).__init__(string)
    
    def equals(self, value, context):
        """Turn ``value`` into a string if it isn't a string yet"""
        value = unicode(value)
        return super(String, self).equals(value, context)
    
    def __unicode__(self):
        """Return the Unicode representation of this constant string."""
        return u'"%s"' % self.constant_value
    
    def __repr__(self):
        """Return the representation for this constant string."""
        return '<String "%s">' % self.constant_value.encode("utf-8")


class Number(Constant):
    """
    Numeric constant.
    
    These constants support inequality operations; see :meth:`greater_than`
    and :meth:`less_than`.
    
    """
    
    operations = Constant.operations | set(['inequality'])
    
    def __init__(self, number):
        """
        
        :param number: The number to be represented, as a Python object.
        :type number: :class:`object`
        
        ``number`` is converted into a :class:`float` internally, so it can
        be an :class:`string <basestring>` initially.
        
        """
        number = float(number)
        super(Number, self).__init__(number)
    
    def equals(self, value, context):
        """
        Check if this numeric constant equals ``value``.
        
        :raises InvalidOperationError: If ``value`` can't be turned into a
            float.
        
        ``value`` will be turned into a float prior to the comparison, to 
        support strings.
        
        """
        return super(Number, self).equals(self._to_number(value), context)
    
    def greater_than(self, value, context):
        """
        Check if this numeric constant is greater than ``value``.
        
        :raises InvalidOperationError: If ``value`` can't be turned into a
            float.
        
        ``value`` will be turned into a float prior to the comparison, to
        support strings.
        
        """
        return self.constant_value > self._to_number(value)
    
    def less_than(self, value, context):
        """
        Check if this numeric constant is less than ``value``.
        
        :raises InvalidOperationError: If ``value`` can't be turned into a
            float.
        
        ``value`` will be turned into a float prior to the comparison, to
        support strings.
        
        """
        return self.constant_value < self._to_number(value)
    
    def _to_number(self, value):
        """
        Convert ``value`` to a Python float and return the new value.
        
        :param value: The value to be converted into float.
        :return: The value as a float.
        :rtype: float
        :raises InvalidOperationError: If ``value`` can't be converted.
        
        """
        try:
            return float(value)
        except ValueError:
            raise InvalidOperationError('"%s" is not a number' % value)
    
    def __unicode__(self):
        """Return the Unicode representation of this constant number."""
        return unicode(self.constant_value)
    
    def __repr__(self):
        """Return the representation for this constant number."""
        return '<Number %s>' % self.constant_value


class Set(Constant):
    """
    Constant sets.
    
    These constants support membership operations; see :meth:`contains` and
    :meth:`is_subset`.
    
    """
    
    operations = Constant.operations | set(["inequality", "membership"])
    
    def __init__(self, *items):
        """
        
        :raises booleano.exc.InvalidOperationError: If at least one of the 
            ``items`` is not an operand.
        
        """
        for item in items:
            if not isinstance(item, Operand):
                raise InvalidOperationError('Item "%s" is not an operand, so '
                                            'it cannot be a member of a set' %
                                            item)
        super(Set, self).__init__(set(items))
    
    def to_python(self, context):
        """
        Return a set made up of the Python representation of the operands
        contained in this set.
        
        """
        items = set(item.to_python(context) for item in self.constant_value)
        return items
    
    def equals(self, value, context):
        """Check if all the items in ``value`` are the same of this set."""
        value = set(value)
        return value == self.to_python(context)
    
    def less_than(self, value, context):
        """
        Check if this set has less items than the number represented in 
        ``value``.
        
        :raises InvalidOperationError: If ``value`` is not an integer.
        
        """
        value = self._to_int(value)
        return len(self.constant_value) < value
    
    def greater_than(self, value, context):
        """
        Check if this set has more items than the number represented in 
        ``value``.
        
        :raises InvalidOperationError: If ``value`` is not an integer.
        
        """
        value = self._to_int(value)
        return len(self.constant_value) > value
    
    def belongs_to(self, value, context):
        """
        Check that this constant set contains the ``value`` item.
        
        """
        for item in self.constant_value:
            try:
                if item.equals(value, context):
                    return True
            except InvalidOperationError:
                continue
        return False
    
    def is_subset(self, value, context):
        """
        Check that the ``value`` set is a subset of this constant set.
        
        """
        for item in value:
            if not self.belongs_to(item, context):
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
    
    def __repr__(self):
        """Return the representation for this constant set."""
        elements = [repr(element) for element in self.constant_value]
        elements = ", ".join(elements)
        if elements:
            elements = " " + elements
        return '<Set%s>' % elements
    
    @classmethod
    def _to_int(cls, value):
        """
        Convert ``value`` is to integer if possible.
        
        :param value: The value to be verified.
        :return: ``value`` as integer.
        :rtype: int
        :raises InvalidOperationError: If ``value`` is not an integer.
        
        This is a workaround for Python < 2.6, where floats didn't have the
        ``.is_integer()`` method.
        
        """
        try:
            value_as_int = int(value)
            is_int = value_as_int == float(value)
        except (ValueError, TypeError):
            is_int = False
        if not is_int:
            raise InvalidOperationError("To compare the amount of items in a "
                                        "set, the operand %s has to be an "
                                        "integer" % repr(value))
        return value_as_int


#}


# Importing the operands so they can be available from this namespace:
from booleano.nodes.operands.classes import Variable, Function
from booleano.nodes.operands.placeholders import (PlaceholderVariable,
                                                  PlaceholderFunction)
