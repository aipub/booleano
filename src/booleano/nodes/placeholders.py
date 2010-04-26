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
Class instance placeholders.

A placeholder operand is an object whose evaluation is not done by Booleano
(i.e., the parse tree is handled directly). As a consequence, the Booleano
parser won't verify its existence.

"""

from booleano.exc import BadCallError
from booleano.nodes.operands import Operand

__all__ = ["PlaceholderVariable", "PlaceholderFunction"]


class PlaceholderInstance(Operand):
    """
    Base class for placeholders of Booleano class instances.
    
    Initially, placeholder operands support all the operations. It's up to the
    converter to verify if the instance is used correctly.
    
    """
    
    def __init__(self, name, namespace_parts=None):
        """
        
        :param name: The name for this placeholder.
        :type name: basestring
        :param namespace_parts: The identifiers in the namespace that contains
            the placeholder.
        :type namespace_parts: tuple
        
        """
        self.name = name.lower()
        self.namespace_parts = tuple(namespace_parts or ())
    
    def __eq__(self, other):
        equivalent = False
        if super(PlaceholderInstance, self).__eq__(other):
            equivalent = (
                self.name == other.name and
                self.namespace_parts == other.namespace_parts
                )
        return equivalent
    
    def _namespace_to_ascii(self):
        """Return the namespace as a single ASCII string."""
        parts = [part.encode("utf-8") for part in self.namespace_parts]
        return ":".join(parts)


class PlaceholderVariable(PlaceholderInstance):
    """
    Placeholder variable.
    
    """
    
    is_leaf = True
    
    def __repr__(self):
        """Return the representation for this placeholder variable."""
        msg = '<Placeholder variable "%s"' % self.name.encode("utf-8")
        if self.namespace_parts:
            ns = self._namespace_to_ascii()
            msg = '%s at namespace="%s"' % (msg, ns)
        return msg + ">"


class PlaceholderFunction(PlaceholderInstance):
    """
    Placeholder for a function call.
    
    """
    
    is_leaf = False
    
    def __init__(self, function_name, namespace_parts=None, *arguments):
        """
        
        :param function_name: The name of the function to be represented.
        :type function_name: basestring
        :param namespace_parts: The identifiers in the namespace that contains
            the placeholder function.
        :type namespace_parts: tuple
        :raises BadCallError: If one of the ``arguments`` is not an
            :class:`Operand`.
        
        """
        for argument in arguments:
            if not isinstance(argument, Operand):
                raise BadCallError(u'Placeholder function "%s" received a '
                                   'non-operand argument: %s' %
                                   (function_name, argument))
        self.arguments = arguments
        super(PlaceholderFunction, self).__init__(function_name,
                                                  namespace_parts)
    
    def __eq__(self, other):
        equivalent = False
        if super(PlaceholderFunction, self).__eq__(other):
            equivalent = self.arguments == other.arguments
        return equivalent
    
    def __repr__(self):
        """Return the representation for this placeholder function."""
        args = [repr(arg) for arg in self.arguments]
        args = ", ".join(args)
        func_name = self.name.encode("utf-8")
        msg = '<Placeholder function call "%s"(%s)' % (func_name, args)
        if self.namespace_parts:
            ns = self._namespace_to_ascii()
            msg = '%s at namespace="%s"' % (msg, ns)
        return msg + ">"

