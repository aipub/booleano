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
Test suite for Booleano nodes.

This module implements utilities to be used in the tests for nodes.

"""

from itertools import chain, permutations, product

from nose.plugins.skip import SkipTest
from nose.tools import assert_not_equal, eq_


__all__ = ["assert_node_equivalence"]


def assert_node_equivalence(*node_groups):
    """
    Assert that each node in a group in ``node_groups`` is equivalent to any
    node of the same group, but different from nodes in other groups.
    
    :raises AssertionError: If two nodes within the same group are not
        equivalent, or if two nodes from different groups are equivalent
    
    ``node_groups`` is an iterable containing groups of nodes. Nodes within the
    same group are expected to be equivalent and also have the same hash.
    
    """
    # TODO: Disabled equivalence tests until nodes become hashable.
    raise SkipTest
    
    for node_group in node_groups:
        # All the nodes within the same group must be equivalent:
        for (node_a, node_b) in permutations(node_group, 2):
            eq_(
                hash(node_a),
                hash(node_b),
                "Nodes %r and %r have the same hash" % (node_a, node_b),
                )
            eq_(
                node_a,
                node_b,
                "Nodes %r and %r are equivalent" % (node_a, node_b),
                )
        
        # A node must be equivalent to itself:
        for node in node_group:
            eq_(
                hash(node),
                hash(node),
                "Node %r has a constant hash" % node,
                )
            eq_(
                node,
                node,
                "Node %r is equivalent to itself" % node,
                )
        
        # Each node in this group must not be equivalent to nodes in other
        # groups:
        different_node_groups = set(node_groups) - set([node_group])
        different_nodes = chain(*different_node_groups)
        inequalities = product(node_group, different_nodes)
        for (node_a, node_b) in inequalities:
            assert_not_equal(
                node_a,
                node_b,
                "Nodes %r and %r are not equivalent" % (node_a, node_b),
                )
