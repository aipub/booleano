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

from nose.tools import assert_false, assert_raises, eq_, ok_, raises

from booleano.exc import BadCallError, BadFunctionError
from booleano.nodes import OperationNode, Function
from booleano.nodes.datatypes import Datatype

from tests.utils.mock_operands import BranchNode, LeafNode, PermissiveFunction


#{ Tests for the base OperationNode class


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
    assert_false(node1 == node2)
    assert_false(node2 == node1)
    ok_(node1 != node2)
    ok_(node2 != node1)


def test_equivalent_nodes():
    """Nodes from the same classes are marked as equivalent."""
    node1 = LeafNode()
    node2 = LeafNode()
    ok_(node1 == node2)
    ok_(node2 == node1)


#{ Tests for the functions


class TestFunctionMeta(object):
    """Tests for the metaclass of the user-defined function nodes."""
    
    def test_arity(self):
        """
        The arity and all the arguments for a function must be calculated
        right after it's been defined.
        
        """
        # Nullary function:
        class NullaryFunction(Function):
            bypass_operation_check = True
        eq_(NullaryFunction.arity, 0)
        eq_(NullaryFunction.all_args, ())
        
        # Unary function:
        class UnaryFunction(Function):
            bypass_operation_check = True
            required_arguments = ("arg1", )
        eq_(UnaryFunction.arity, 1)
        eq_(UnaryFunction.all_args, ("arg1", ))
        
        # Unary function, with its argument optional:
        class OptionalUnaryFunction(Function):
            bypass_operation_check = True
            optional_arguments = {'oarg1': LeafNode()}
        eq_(OptionalUnaryFunction.arity, 1)
        eq_(OptionalUnaryFunction.all_args, ("oarg1", ))
        
        # Binary function:
        class BinaryFunction(Function):
            bypass_operation_check = True
            required_arguments = ("arg1", )
            optional_arguments = {'oarg1': LeafNode()}
        eq_(BinaryFunction.arity, 2)
        eq_(BinaryFunction.all_args, ("arg1", "oarg1"))
    
    @raises(BadFunctionError)
    def test_duplicate_arguments(self):
        """An optional argument shouldn't share its name with a required one"""
        class FunctionWithDuplicateArguments(Function):
            required_arguments = ("arg1", )
            optional_arguments = {'arg1': None}
    
    @raises(BadFunctionError)
    def test_duplicate_required_arguments(self):
        """Two required arguments must not share the same name."""
        class FunctionWithDuplicateArguments(Function):
            required_arguments = ("arg1", "arg1")
    
    @raises(BadFunctionError)
    def test_non_node_default_arguments(self):
        """Default values for the optional arguments must be operation nodes."""
        class FunctionWithNonOperands(Function):
            bypass_operation_check = True
            optional_arguments = {'arg': 1}


class TestFunction(object):
    """Tests for the base class of user-defined function nodes."""
    
    def test_node_type(self):
        """Functions are branch nodes."""
        func = PermissiveFunction(LeafNode())
        ok_(func.is_branch)
        assert_false(func.is_leaf)
    
    def test_constructor_with_minimum_arguments(self):
        func = PermissiveFunction(LeafNode("baz"))
        args = {
            'arg0': LeafNode("baz"),
            'oarg0': LeafNode("foo"),
            'oarg1': BranchNode("bar"),
        }
        eq_(func.arguments, args)
    
    def test_constructor_with_one_optional_argument(self):
        func = PermissiveFunction(LeafNode("this-is-arg0"),
                                  LeafNode("this-is-oarg0"))
        args = {
            'arg0': LeafNode("this-is-arg0"),
            'oarg0': LeafNode("this-is-oarg0"),
            'oarg1': BranchNode("bar"),
        }
        eq_(func.arguments, args)
    
    def test_constructor_with_all_arguments(self):
        func = PermissiveFunction(
            BranchNode("this-is-arg0"),
            LeafNode("this-is-oarg0"),
            BranchNode("this-is-oarg1"),
        )
        args = {
            'arg0': BranchNode("this-is-arg0"),
            'oarg0': LeafNode("this-is-oarg0"),
            'oarg1': BranchNode("this-is-oarg1"),
        }
        eq_(func.arguments, args)
    
    @raises(BadCallError)
    def test_constructor_with_few_arguments(self):
        PermissiveFunction()
    
    @raises(BadCallError)
    def test_constructor_with_many_arguments(self):
        PermissiveFunction(
            LeafNode(0),
            LeafNode(1),
            LeafNode(2),
            LeafNode(3),
            LeafNode(4),
            LeafNode(5),
            LeafNode(6),
            LeafNode(7),
            LeafNode(8),
            LeafNode(9),
        )
    
    def test_constructor_accepts_operands(self):
        """Only operands are valid function arguments."""
        PermissiveFunction(LeafNode(), BranchNode())
        assert_raises(BadCallError, PermissiveFunction, None)
        assert_raises(BadCallError, PermissiveFunction, 2)
        assert_raises(BadCallError, PermissiveFunction, Datatype())
    
    def test_no_argument_validation_by_default(self):
        """
        Arguments must be explicitly validated by the function.
        
        This is, their .check_arguments() method must be overriden.
        
        """
        class MockFunction(Function):
            bypass_operation_check = True
            __eq__ = lambda other: False
        assert_raises(NotImplementedError, MockFunction)
    
    def test_equivalence(self):
        """
        Two functions are equivalent not only if they share the same class,
        but also if their arguments are equivalent.
        
        """
        class FooFunction(Function):
            bypass_operation_check = True
            required_arguments = ("abc", )
            optional_arguments = {"xyz": LeafNode("123")}
            
            def __eq__(self, other):
                return super(FooFunction, self).__eq__(other)
            
            def check_arguments(self):
                pass
        
        func1 = FooFunction(LeafNode("whatever"))
        func2 = FooFunction(LeafNode("whatever"))
        func3 = PermissiveFunction(BranchNode("baz"))
        func4 = PermissiveFunction(LeafNode("foo"))
        func5 = FooFunction(LeafNode("something"))
        
        ok_(func1 == func1)
        ok_(func1 == func2)
        assert_false(func1 == func3)
        assert_false(func1 == func4)
        assert_false(func1 == func5)
        ok_(func2 == func1)
        ok_(func2 == func2)
        assert_false(func2 == func3)
        assert_false(func2 == func4)
        assert_false(func2 == func5)
        assert_false(func3 == func1)
        assert_false(func3 == func2)
        ok_(func3 == func3)
        assert_false(func3 == func4)
        assert_false(func3 == func5)
        assert_false(func4 == func1)
        assert_false(func4 == func2)
        assert_false(func4 == func3)
        ok_(func4 == func4)
        assert_false(func4 == func5)
        assert_false(func5 == func1)
        assert_false(func5 == func2)
        assert_false(func5 == func3)
        assert_false(func5 == func4)
        ok_(func5 == func5)
    
    def test_representation(self):
        func = PermissiveFunction(LeafNode("foo"), BranchNode(u"fú"))
        expected = "<Anonymous function call [PermissiveFunction] " \
                   "arg0=LeafNode('foo'), oarg0=BranchNode(u'f\\xfa'), " \
                   "oarg1=BranchNode('bar')>"
        eq_(repr(func), expected)


#}
