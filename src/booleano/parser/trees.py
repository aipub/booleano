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
Parse trees.

Booleano supports two kinds of parse trees:
- *Evaluable parse trees*, which are truth-evaluated against so-called helpers.
- *Convertible parse trees*, which are converted into something else (e.g.,
  SQL "WHERE" clauses) using so-called parse tree converters.

"""

from booleano.operations import Truth

__all__ = ("EvaluableParseTree", "ConvertibleParseTree")


class ParseTree(object):
    """
    Base class for parse trees.
    
    """
    
    def __init__(self, root_node):
        """
        Instantiate a parse tree whose root node is ``root_node``.
        
        :param root_node: The root node of the parse tree.
        :type root_node: ParseTreeNode
        
        """
        self.root_node = root_node


class EvaluableParseTree(ParseTree):
    """
    Truth-evaluable parse tree.
    
    """
    
    def __init__(self, root_node):
        """
        Wrap ``root_node`` into the truth function.
        
        :raises InvalidOperationError: If the ``root_node`` is an operand that
            doesn't support logical values.
        
        """
        root_node = Truth.convert(root_node)
        super(EvaluableParseTree, self).__init__(root_node)
    
    def __call__(self, **helpers):
        """
        Check if the parse tree evaluates to True with the context described by
        the ``helpers``.
        
        :return: Whether the parse tree evaluates to True.
        :rtype: bool
        
        """
        return self.root_node(**helpers)


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
        
        """
        return converter(self.root_node)
