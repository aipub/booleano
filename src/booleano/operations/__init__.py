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
Supported operations represented in Python objects.

In other words, this package contains the elements of the parse trees.

Once parsed, the binary expressions are turned into the relevant operation
using the classes provided by this package.

"""

__all__ = ["OPERATIONS", "ParseTreeNode"]


# Byte flag for the base operations:
OPERATIONS = set((
    "equality",           # ==, !=
    "inequality",         # >, <, >=, <=
    "boolean",            # Logical values
    "membership",         # Set operations (i.e., ∈ and ⊂)
))


class ParseTreeNode(object):
    """
    Base class for the individual elements available in parse trees (i.e.,
    operands and operations).
    
    """
    
    def check_equivalence(self, node):
        """
        Make sure ``node`` and this node are equivalent.
        
        :param node: The other node which may be equivalent to this one.
        :type node: ParseTreeNode
        :raises AssertionError: If both nodes have different classes.
        
        Operands and operations must extend this method to check for other
        attributes specific to such nodes.
        
        """
        error_msg = 'Nodes "%s" and "%s" are not equivalent'
        assert isinstance(node, self.__class__), error_msg % (node, self)
    
    def __eq__(self, other):
        """
        Check if the ``other`` node is equivalent to this one.
        
        :return: Whether they are equivalent.
        :rtype: bool
        
        """
        try:
            self.check_equivalence(other)
            return True
        except AssertionError:
            return False
    
    def __ne__(self, other):
        """
        Check if the ``other`` node is not equivalent to this one.
        
        :return: Whether they are not equivalent.
        :rtype: bool
        
        """
        try:
            self.check_equivalence(other)
            return False
        except AssertionError:
            return True
    
    def __str__(self):
        """
        Return the ASCII representation of this node.
        
        :raises NotImplementedError: If the Unicode representation is not
            yet implemented.
        
        If it contains non-English characters, they'll get converted into ASCII
        into ugly things -- It's best to use the Unicode representation
        directly.
        
        """
        as_unicode = self.__unicode__()
        return str(as_unicode.encode("utf-8"))
    
    def __unicode__(self):
        """
        Return the Unicode representation for this node.
        
        :raises NotImplementedError: If the Unicode representation is not
            yet implemented.
        
        """
        raise NotImplementedError("Node %s doesn't have an Unicode "
                                  "representation" % type(self))

