# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://booleano.efous.org/>.
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
Unit tests for the base class of the nodes.

"""

from nose.tools import ok_, assert_false, assert_raises

from booleano.nodes import OperationNode


#{ Tests


def test_abstractness():
    """The base operation node cannot be instantiated directly."""
    assert_raises(TypeError, OperationNode)


def test_branch():
    """Nodes are marked as branch when appropriate."""
    leaf = LeafNode()
    branch = BranchNode()
    assert_false(leaf.is_branch)
    ok_(branch.is_branch)


def test_different_nodes():
    """Nodes from different classes are not marked as equivalent."""
    node1 = LeafNode()
    node2 = BranchNode()
    assert_false(node1.is_equivalent(node2))
    assert_false(node2.is_equivalent(node1))
    assert_false(node1 == node2)
    assert_false(node2 == node1)
    ok_(node1 != node2)
    ok_(node2 != node1)


def test_equivalent_nodes():
    """Nodes from the same classes are marked as equivalent."""
    node1 = LeafNode()
    node2 = LeafNode()
    ok_(node1.is_equivalent(node2))
    ok_(node2.is_equivalent(node1))
    ok_(node1 == node2)
    ok_(node2 == node1)
    assert_false(node1 != node2)
    assert_false(node2 != node1)


#{ Mock and useless nodes


class MockNodeBase(OperationNode):
    
    def is_equivalent(self, node):
        return super(MockNodeBase, self).is_equivalent(node)
    
    def __repr__(self):
        return "%s()" % self.__class__.__name__


class LeafNode(MockNodeBase):
    
    is_leaf = True


class BranchNode(MockNodeBase):
    
    is_leaf = False


#}
