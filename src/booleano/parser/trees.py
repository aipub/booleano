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
Parse trees.

Booleano supports two kinds of parse trees:

* **Evaluable parse trees**, which are truth-evaluated against so-called
  context.
* **Convertible parse trees**, which are converted into something else (e.g.,
  SQL "WHERE" clauses) using so-called parse tree converters.

"""

__all__ = ("EvaluableParseTree", "ConvertibleParseTree")


class ParseTree(object):
    """
    Base class for parse trees.
    
    """
    
    def __init__(self, root_node):
        """
        
        :param root_node: The root node of the parse tree.
        :type root_node: :class:`booleano.nodes.OperationNode`
        
        """
        self.root_node = root_node
    
    def __eq__(self, other):
        """
        Check if the ``other`` parse tree is equivalent to this one.
        
        """
        return (isinstance(other, self.__class__) and
                other.root_node == self.root_node)
    
    def __ne__(self, other):
        """
        Check if the ``other`` parse tree is **not** equivalent to this one.
        
        """
        return not self.__eq__(other)


class EvaluableParseTree(ParseTree):
    """
    Truth-evaluable parse tree.
    
    """
    
    def __init__(self, root_node):
        """
        
        :param root_node: The root node of the parse tree.
        :type root_node: :class:`booleano.nodes.OperationNode`
        :raises booleano.exc.InvalidOperationError: If the ``root_node`` is an 
            operand that doesn't support logical values.
        
        """
        root_node.check_logical_support()
        super(EvaluableParseTree, self).__init__(root_node)
    
    def __call__(self, context):
        """
        Check if the parse tree evaluates to True with the context described by
        the ``context``.
        
        :return: Whether the parse tree evaluates to True.
        :rtype: bool
        
        """
        return self.root_node(context)
    
    def __unicode__(self):
        """Return the Unicode representation for this tree."""
        return "Evaluable parse tree (%s)" % unicode(self.root_node)
    
    def __repr__(self):
        """Return the representation for this tree."""
        return "<Parse tree (evaluable) %s>" % repr(self.root_node)


class ConvertibleParseTree(ParseTree):
    """
    Convertible parse tree.
    
    """
    
    def __call__(self, converter):
        """
        Convert the parse tree with ``converter``.
        
        :param converter: The converter to be used.
        :type converter: booleano.converters.BaseConverter
        :return: The conversion result.
        :rtype: object
        
        """
        return converter(self.root_node)
    
    def __unicode__(self):
        """Return the Unicode representation for this tree."""
        return "Convertible parse tree (%s)" % unicode(self.root_node)
    
    def __repr__(self):
        """Return the representation for this tree."""
        return "<Parse tree (convertible) %s>" % repr(self.root_node)
