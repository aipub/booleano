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
Booleano constants.

"""

from booleano.exc import InvalidOperationError
from booleano.nodes import OperationNode
from booleano.nodes.datatypes import NumberType, SetType, StringType


__all__ = ["Constant", "String", "Number", "Set"]


#{ Built-in constants


class Constant(OperationNode):
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
    
    def __init__(self, constant_value):
        """
        
        :param constant_value: The Python value represented by the Booleano
            constant.
        :type constant_value: :class:`object`
        
        """
        self._constant_value = constant_value
    
    def __eq__(self, other):
        equivalent = False
        if super(Constant, self).__eq__(other):
            equivalent = other._constant_value == self._constant_value
        return equivalent


class String(Constant, StringType):
    """
    Constant string.
    
    """
    
    is_leaf = True
    
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
    
    def get_as_string(self, context):
        return self._constant_value
    
    def __repr__(self):
        return '<String "%s">' % self._constant_value.encode("utf-8")


class Number(Constant, NumberType):
    """
    Numeric constant.
    
    These constants support inequality operations; see :meth:`greater_than`
    and :meth:`less_than`.
    
    """
    
    is_leaf = True
    
    def __init__(self, number):
        """
        
        :param number: The number to be represented, as a Python object.
        :type number: :class:`object`
        
        ``number`` is converted into a :class:`float` internally, so it can
        be an :class:`string <basestring>` initially.
        
        """
        number = float(number)
        super(Number, self).__init__(number)
    
    def get_as_number(self, context):
        return self._constant_value
    
    def __repr__(self):
        return '<Number %s>' % self._constant_value


class Set(Constant, SetType):
    """
    Constant sets.
    
    These constants support membership operations; see :meth:`contains` and
    :meth:`is_subset`.
    
    """
    
    is_leaf = False
    
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
        items = set(item.to_python(context) for item in self._constant_value)
        return items
    
    def __repr__(self):
        """Return the representation for this constant set."""
        elements = [repr(element) for element in self._constant_value]
        elements = ", ".join(elements)
        if elements:
            elements = " " + elements
        return '<Set%s>' % elements


#}

