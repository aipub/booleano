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
