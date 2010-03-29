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

"""

from abc import ABCMeta, abstractmethod

__all__ = ("Datatype", "Boolean", "Number", "String", "Set")


class Datatype(object):
    """
    Base interface for Booleano datatypes.
    
    """
    
    __metaclass__ = ABCMeta


class Boolean(Datatype):
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


class Number(Datatype):
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


class String(Datatype):
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


class Set(Datatype):
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

