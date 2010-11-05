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
Booleano datatypes (not to be confused with *Python datatypes*).

They are an interface between the value users intend to represent through
Booleano and the actual Python values.

TODO: Rename "__booleano_base_types__" to "__booleano_supertypes__".

"""

from abc import ABCMeta, abstractmethod
from inspect import getmro


__all__ = ["get_supertype", "Datatype", "BooleanType", "NumberType",
           "StringType", "SetType"]


# TODO:
def get_supertype(*datatypes):
    """
    Return the supertype of the ``datatypes``.
    
    :return: The supertype class, or ``None`` if there's no common ancestor
        among the ``datatypes`` or there's more than one supertype.
    :rtype: :class:`Datatype`
    
    """
    pass


class _DatatypeMeta(ABCMeta):
    """
    Metaclass for Booleano datatypes.
    
    It sets the class attribute :attr:`__booleano_base_types__` on the datatype
    implementation classes, to the Booleano datatypes being implemented.
    
    """
    
    def __new__(cls, name, bases, ns):
        datatype = super(_DatatypeMeta, cls).__new__(cls, name, bases, ns)
        
        # Calculating the Booleano datatypes among the base classes:
        if "__booleano_base_types__" not in ns:
            base_types = []
            for base_type in getmro(datatype)[1:]:
                if issubclass(base_type, Datatype) and base_type != Datatype:
                    base_types.append(base_type)
            datatype.__booleano_base_types__ = base_types
        
        return datatype


class Datatype(object):
    """
    Base interface for Booleano datatypes.
    
    """
    
    __metaclass__ = _DatatypeMeta
    
    __booleano_base_types__ = None


class BooleanType(Datatype):
    """
    Interface for logical values.
    
    """
    
    @abstractmethod
    def get_as_boolean(self, context):   #pragma: no cover
        """
        Return the Python boolean equivalent for this node.
        
        :param context: The context against which the node will be evaluated.
        :return: The Python boolean equivalent.
        :rtype: :class:`bool`
        
        """
        pass
    
    def __call__(self, context):
        """Alias for :meth:`get_as_boolean`."""
        return self.get_as_boolean(context)


class NumberType(Datatype):
    """
    Interface for numeric values.
    
    """
    
    @abstractmethod
    def get_as_number(self, context):   #pragma: no cover
        """
        Return the Python float equivalent for this node.
        
        :param context: The context against which the node will be evaluated.
        :return: The Python float equivalent.
        :rtype: :class:`float`
        
        """
        pass


class StringType(Datatype):
    """
    Interface for character strings.
    
    """
    
    @abstractmethod
    def get_as_string(self, context):   #pragma: no cover
        """
        Return the Python string equivalent for this node.
        
        :param context: The context against which the node will be evaluated.
        :return: The Python string equivalent.
        :rtype: :class:`basestring`
        
        """
        pass


# It's tempting to make sets a kind of numbers, so that inequality operations
# work out-of-the-box, but sometimes it may not be the right thing. It's best
# to leave it up to the user.
class SetType(Datatype):
    """
    Interface for sets.
    
    """
    
    @abstractmethod
    def get_as_set(self, context):   #pragma: no cover
        """
        Return the Python set equivalent for this node.
        
        :param context: The context against which the node will be evaluated.
        :return: The Python set equivalent.
        :rtype: :class:`set`
        
        """
        pass

