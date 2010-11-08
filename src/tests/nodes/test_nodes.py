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
from booleano.nodes.datatypes import Datatype, BooleanType, NumberType

from tests.nodes import assert_node_equivalence
from tests.utils.mock_nodes import (BoolVar, BranchNode, LeafNode, NumVar,
    PermissiveFunction, TrafficLightVar)


#{ Tests for the base OperationNode class
# TODO: Move individual test functions into a TestCase.


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


def test_hash():
    """By default, the hash of a node is the hash of its class."""
    node = LeafNode()
    eq_(hash(node), hash(LeafNode))


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
            pass
        eq_(NullaryFunction.arity, 0)
        eq_(NullaryFunction.all_args, ())
        
        # Unary function:
        class UnaryFunction(Function):
            required_arguments = ("arg1", )
        eq_(UnaryFunction.arity, 1)
        eq_(UnaryFunction.all_args, ("arg1", ))
        
        # Unary function, with its argument optional:
        class OptionalUnaryFunction(Function):
            optional_arguments = {'oarg1': LeafNode()}
        eq_(OptionalUnaryFunction.arity, 1)
        eq_(OptionalUnaryFunction.all_args, ("oarg1", ))
        
        # Binary function:
        class BinaryFunction(Function):
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
            optional_arguments = {'arg': 1}
    
    #{ Argument types
    
    def test_argument_types_for_all_known_arguments(self):
        """Argument types can only be set for known arguments"""
        class StronglyTypedFunction(Function):
            required_arguments = ("arg1", "arg2")
            argument_types = {'arg1': BooleanType, 'arg2': NumberType}
    
    def test_homogeneous_argument_types(self):
        """The argument types can be set once if they're all the same"""
        class StronglyTypedFunction(Function):
            required_arguments = ("arg1", "arg2")
            argument_types = BooleanType
    
    def test_argument_types_for_some_known_arguments(self):
        """Argument types may be set for some (not all) known arguments"""
        class StronglyTypedFunction1(Function):
            required_arguments = ("arg1", )
            argument_types = {'arg1': BooleanType}
            
        class StronglyTypedFunction2(Function):
            required_arguments = ("arg1", )
            optional_arguments = {'arg2': BoolVar()}
            argument_types = {'arg1': BooleanType, 'arg2': BooleanType}
    
    @raises(BadFunctionError)
    def test_argument_types_for_unknown_arguments(self):
        """Argument types may not be set for unknown arguments"""
        class StronglyTypedFunction(Function):
            required_arguments = ("arg1", "arg2")
            argument_types = {'arg3': BooleanType}
    
    @raises(BadFunctionError)
    def test_invalid_argument_types(self):
        """Argument types must be either a mapping or a datatype"""
        class StronglyTypedFunction(Function):
            required_arguments = ("arg1", "arg2")
            argument_types = object()
    
    #{ Commutativity
    
    def test_non_commutative_by_default(self):
        """Functions are non-commutative by default."""
        class MyFunction(Function):
            pass
        
        assert_false(MyFunction.is_commutative)
    
    @raises(BadFunctionError)
    def test_no_argument_types_in_commutative_functions(self):
        """The types of the arguments in a commutative function must be set."""
        class MyFunction(Function):
            is_commutative = True
    
    @raises(BadFunctionError)
    def test_different_argument_types_in_commutative_functions(self):
        """
        The types of the arguments in a commutative function must be the same.
        
        """
        class MyFunction(Function):
            required_arguments = ("arg1", "arg2")
            argument_types = {'arg1': BooleanType, 'arg2': NumberType}
            is_commutative = True
    
    #}


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
    
    def test_valid_argument_type(self):
        """Only arguments that implement the expected datatype are accepted."""
        class StronglyTypedFunction(Function):
            required_arguments = ("arg1", "arg2")
            argument_types = {'arg1': BooleanType, 'arg2': NumberType}
        
        StronglyTypedFunction(BoolVar(), NumVar())
        # Now arguments with the wrong types:
        assert_raises(BadCallError, StronglyTypedFunction, BoolVar(), BoolVar())
        assert_raises(BadCallError, StronglyTypedFunction, NumVar(), NumVar())
        assert_raises(BadCallError, StronglyTypedFunction, NumVar(), BoolVar())
    
    def test_homogeneouos_argument_types(self):
        """
        The argument types can be set just once if it's the same for all the
        arguments.
        
        """
        class StronglyTypedFunction(Function):
            required_arguments = ("arg1", "arg2")
            argument_types = BooleanType
        
        StronglyTypedFunction(BoolVar(), BoolVar())
        # Now arguments with the wrong types:
        assert_raises(BadCallError, StronglyTypedFunction, NumVar(), BoolVar())
        assert_raises(BadCallError, StronglyTypedFunction, BoolVar(), NumVar())
        assert_raises(BadCallError, StronglyTypedFunction, NumVar(), NumVar())
    
    def test_no_expected_datatype(self):
        """
        All the arguments are accepted if there's no expected type for them.
        
        """
        class WeaklyTypedFunction(Function):
            required_arguments = ("arg1", "arg2")
        
        WeaklyTypedFunction(BoolVar(), NumVar())
        WeaklyTypedFunction(BoolVar(), BoolVar())
        WeaklyTypedFunction(NumVar(), NumVar())
        WeaklyTypedFunction(NumVar(), BoolVar())
    
    def test_equivalence(self):
        """
        Two function calls are equivalent not only if they share the same class,
        but also if their arguments are equivalent.
        
        """
        class FooFunction(Function):
            required_arguments = ("abc", )
            optional_arguments = {"xyz": LeafNode("123")}
        
        class CommutativeFunction(Function):
            required_arguments = range(2)
            argument_types = BooleanType
            is_commutative = True
        
        func1 = FooFunction(LeafNode("whatever"))
        func2 = FooFunction(LeafNode("whatever"))
        func3 = PermissiveFunction(BranchNode("baz"))
        func4 = PermissiveFunction(LeafNode("foo"))
        func5 = FooFunction(LeafNode("something"))
        func6 = CommutativeFunction(BoolVar(), TrafficLightVar())
        func7 = CommutativeFunction(TrafficLightVar(), BoolVar())
        
        assert_node_equivalence(
            (func1, func2),
            (func3, ),
            (func4, ),
            (func5, ),
            (func6, func7),
            )
    
    def test_representation(self):
        func = PermissiveFunction(LeafNode("foo"), BranchNode(u"fú"))
        expected = "<Anonymous function call [PermissiveFunction] " \
                   "arg0=LeafNode('foo'), oarg0=BranchNode(u'f\\xfa'), " \
                   "oarg1=BranchNode('bar')>"
        eq_(repr(func), expected)
    
    def test_hash_nullary(self):
        """The hash of a nullary function is the hash of the function class."""
        func = TrafficLightVar()
        eq_(hash(func), hash(TrafficLightVar))
    
    def test_hash_with_arguments(self):
        """The hash of a function also uses the hash of the arguments."""
        arg1 = LeafNode("foo")
        arg2 = BranchNode(u"fú")
        arg3 = LeafNode("bar")
        func = PermissiveFunction(arg1, arg2, arg3)
        
        args_hash = hash(arg1) + hash(arg2) + hash(arg3)
        expected_hash = hash(PermissiveFunction) + args_hash
        
        eq_(hash(func), expected_hash)


#}
