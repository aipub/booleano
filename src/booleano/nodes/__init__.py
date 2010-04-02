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
Operation nodes.

They represent the parse tree when a boolean expression has been parsed.

"""

from abc import ABCMeta, abstractmethod, abstractproperty


__all__ = ("OperationNode", "OPERATIONS")


#: The known/supported operations.
OPERATIONS = set((
    "equality",           # ==, !=
    "inequality",         # >, <, >=, <=
    "boolean",            # Logical values
    "membership",         # Set operations (i.e., ∈ and ⊂)
))


class OperationNode(object):
    """
    Base class for the operation nodes.
    
    """
    
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def is_leaf(self):   #pragma: no cover
        """
        Report whether this is a leaf node.
        
        :rtype: bool
        
        Leaf nodes are those which don't contain other nodes.
        
        """
        pass
    
    @property
    def is_branch(self):
        """
        Report whether this is a branch node.
        
        :rtype: bool
        
        Branch nodes are those which contain other nodes.
        
        """
        return not self.is_leaf
    
    @abstractmethod
    def __eq__(self, other):
        """
        Report whether ``other`` is a node and is equivalent with this one.
        
        :param node: The other node which may be equivalent to this one.
        :type node: :class:`OperationNode`
        :rtype: :class:`bool`
        
        """
        return type(self) == type(other)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    @abstractmethod
    def __repr__(self):   #pragma: no cover
        pass

