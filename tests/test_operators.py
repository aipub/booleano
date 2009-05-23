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
Tests for the operands.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises, raises

from booleano.operations.operators import *
from booleano.operations.operands import String, Number, Set, Variable
from booleano.exc import InvalidOperationError, BadCallError, BadFunctionError

from tests import (TrafficLightVar, PedestriansCrossingRoad,
                   DriversAwaitingGreenLightVar, TrafficViolationFunc)


class TestFunctions(object):
    """Tests for the base class of user-defined function operators."""
    
    def test_no_language_specific_names(self):
        func = PermissiveFunction("greeting", "arg0")
        eq_("greeting", func.global_name)
        eq_({}, func.names)
    
    def test_with_language_specific_names(self):
        """
        There are no language-specific names defined by default.
        
        """
        names = {
            'fr': "bonjour",
            'en': "hi",
            'es': "hello",
        }
        func = PermissiveFunction("greeting", "arg0", **names)
        eq_(names, func.names)
    
    def test_with_default_language_specific_names(self):
        """
        Functions can be created with default names in any language.
        
        """
        class GreetingFunction(PermissiveFunction):
            default_names = {'fr': "bonjour"}
        
        # Appending names:
        func = GreetingFunction("greet", "arg0", en="hi", es="hola")
        eq_({'fr': "bonjour", 'en': "hi", 'es': "hola"}, func.names)
        # Appending and replacing names:
        func = GreetingFunction("greet", "arg0", fr="salut", es="hola")
        eq_({'fr': "salut", 'es': "hola"}, func.names)
    
    def test_with_default_case_insensitive_names(self):
        """
        The default names are case insensitive.
        
        """
        class GreetingFunction(PermissiveFunction):
            default_names = {'fr': "BONJOUR", 'es': "HOLA", 'en': "hello"}
        
        func = GreetingFunction("GREET", "arg0")
        eq_(func.global_name, "greet")
        eq_({'fr': "bonjour", 'en': "hello", 'es': "hola"},
            GreetingFunction.default_names)
    
    def test_constructor_with_minimum_arguments(self):
        func = PermissiveFunction("permissive", "this-is-arg0")
        args = {
            'arg0': "this-is-arg0",
            'oarg0': None,
            'oarg1': 1
        }
        eq_(func.arguments, args)
    
    def test_constructor_with_one_optional_argument(self):
        func = PermissiveFunction("permissive", "this-is-arg0",
                                  "this-is-oarg0")
        args = {
            'arg0': "this-is-arg0",
            'oarg0': "this-is-oarg0",
            'oarg1': 1
        }
        eq_(func.arguments, args)
    
    def test_constructor_with_all_arguments(self):
        func = PermissiveFunction("permissive", "this-is-arg0", "this-is-oarg0",
                                  "this-is-oarg1")
        args = {
            'arg0': "this-is-arg0",
            'oarg0': "this-is-oarg0",
            'oarg1': "this-is-oarg1"
        }
        eq_(func.arguments, args)
    
    @raises(BadCallError)
    def test_constructor_with_few_arguments(self):
        PermissiveFunction("permissive", )
    
    @raises(BadCallError)
    def test_constructor_with_many_arguments(self):
        PermissiveFunction("permissive", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    
    def test_no_validation_by_default(self):
        """
        Arguments must be explicitly validated by the function.
        
        This is, their .check_arguments() method must be overriden.
        
        """
        class MockFunction(FunctionOperator): pass
        assert_raises(NotImplementedError, MockFunction, "mock")
    
    def test_evaluation_not_implemented(self):
        """Expression evaluation must *not* be available by default"""
        class FakeFunction(FunctionOperator):
            def check_arguments(self):
                pass
        
        func = FakeFunction("fake")
        assert_raises(NotImplementedError, func)
    
    def test_checking_supported_operation(self):
        # Setting it up
        operand = String("valencia")
        class FakeFunction(FunctionOperator):
            """Fake function to proxy Operator.check_operation()."""
            pass
        # Testing it
        FakeFunction.check_operation(operand, "equality")
        assert_raises(InvalidOperationError, FakeFunction.check_operation,
                      operand, "boolean")
        assert_raises(InvalidOperationError, FakeFunction.check_operation,
                      operand, "inequality")
        assert_raises(InvalidOperationError, FakeFunction.check_operation,
                      operand, "membership")
    
    def test_arity(self):
        """
        The arity and all the arguments for a function must be calculated
        right after it's been defined.
        
        """
        # Nullary function:
        class NullaryFunction(FunctionOperator): pass
        eq_(NullaryFunction.arity, 0)
        eq_(NullaryFunction.all_args, ())
        
        # Unary function:
        class UnaryFunction(FunctionOperator):
            required_arguments = ("arg1", )
        eq_(UnaryFunction.arity, 1)
        eq_(UnaryFunction.all_args, ("arg1", ))
        
        # Unary function, with its argument optional:
        class OptionalUnaryFunction(FunctionOperator):
            optional_arguments = {'oarg1': None}
        eq_(OptionalUnaryFunction.arity, 1)
        eq_(OptionalUnaryFunction.all_args, ("oarg1", ))
        
        # Binary function:
        class BinaryFunction(FunctionOperator):
            required_arguments = ("arg1", )
            optional_arguments = {'oarg1': None}
        eq_(BinaryFunction.arity, 2)
        eq_(BinaryFunction.all_args, ("arg1", "oarg1"))
    
    @raises(BadFunctionError)
    def test_duplicate_arguments(self):
        """An optional argument shouldn't share its name with a required one"""
        class FunctionWithDuplicateArguments(FunctionOperator):
            required_arguments = ("arg1", )
            optional_arguments = {'arg1': None}
    
    @raises(BadFunctionError)
    def test_duplicate_required_arguments(self):
        """Two required arguments must not share the same name."""
        class FunctionWithDuplicateArguments(FunctionOperator):
            required_arguments = ("arg1", "arg1")
    
    def test_equivalence(self):
        """
        Two functions are equivalent if they share the name, the required
        and optional arguments, and the actual arguments passed.
        
        """
        class FooFunction(FunctionOperator):
            required_arguments = ("abc", )
            optional_arguments = {"xyz": "123"}
            def check_arguments(self): pass
        
        func1 = FooFunction("foo", "whatever")
        func2 = FooFunction("foo", "whatever")
        func3 = TrafficViolationFunc("traffic_violation", "pedestrians",
                                     es=u"peatón")
        func4 = PermissiveFunction("permissive", "foo")
        func5 = FooFunction("foo", "something")
        func6 = FooFunction("bar", "whatever")
        func7 = TrafficViolationFunc("TRAFFIC_VIOLATION", "pedestrians",
                                     es=u"PEATÓN")
        
        func1.check_equivalence(func2)
        func2.check_equivalence(func1)
        func3.check_equivalence(func7)
        func7.check_equivalence(func3)
        
        assert_raises(AssertionError, func1.check_equivalence, func3)
        assert_raises(AssertionError, func1.check_equivalence, func4)
        assert_raises(AssertionError, func1.check_equivalence, func5)
        assert_raises(AssertionError, func1.check_equivalence, func6)
        assert_raises(AssertionError, func1.check_equivalence, func7)
        assert_raises(AssertionError, func2.check_equivalence, func3)
        assert_raises(AssertionError, func2.check_equivalence, func4)
        assert_raises(AssertionError, func2.check_equivalence, func5)
        assert_raises(AssertionError, func2.check_equivalence, func6)
        assert_raises(AssertionError, func2.check_equivalence, func7)
        assert_raises(AssertionError, func3.check_equivalence, func1)
        assert_raises(AssertionError, func3.check_equivalence, func2)
        assert_raises(AssertionError, func3.check_equivalence, func4)
        assert_raises(AssertionError, func3.check_equivalence, func5)
        assert_raises(AssertionError, func3.check_equivalence, func6)
        assert_raises(AssertionError, func4.check_equivalence, func1)
        assert_raises(AssertionError, func4.check_equivalence, func2)
        assert_raises(AssertionError, func4.check_equivalence, func3)
        assert_raises(AssertionError, func4.check_equivalence, func5)
        assert_raises(AssertionError, func4.check_equivalence, func6)
        assert_raises(AssertionError, func4.check_equivalence, func7)
        assert_raises(AssertionError, func5.check_equivalence, func1)
        assert_raises(AssertionError, func5.check_equivalence, func2)
        assert_raises(AssertionError, func5.check_equivalence, func3)
        assert_raises(AssertionError, func5.check_equivalence, func4)
        assert_raises(AssertionError, func5.check_equivalence, func6)
        assert_raises(AssertionError, func5.check_equivalence, func7)
        assert_raises(AssertionError, func6.check_equivalence, func1)
        assert_raises(AssertionError, func6.check_equivalence, func2)
        assert_raises(AssertionError, func6.check_equivalence, func3)
        assert_raises(AssertionError, func6.check_equivalence, func4)
        assert_raises(AssertionError, func6.check_equivalence, func5)
        assert_raises(AssertionError, func6.check_equivalence, func7)
        assert_raises(AssertionError, func7.check_equivalence, func1)
        assert_raises(AssertionError, func7.check_equivalence, func2)
        assert_raises(AssertionError, func7.check_equivalence, func4)
        assert_raises(AssertionError, func7.check_equivalence, func5)
        assert_raises(AssertionError, func7.check_equivalence, func6)
        
        ok_(func1 == func2)
        ok_(func2 == func1)
        ok_(func3 == func7)
        ok_(func7 == func3)
        ok_(func1 != func3)
        ok_(func1 != func4)
        ok_(func1 != func5)
        ok_(func1 != func6)
        ok_(func1 != func7)
        ok_(func2 != func3)
        ok_(func2 != func4)
        ok_(func2 != func5)
        ok_(func2 != func6)
        ok_(func2 != func7)
        ok_(func3 != func1)
        ok_(func3 != func2)
        ok_(func3 != func4)
        ok_(func3 != func5)
        ok_(func3 != func6)
        ok_(func4 != func1)
        ok_(func4 != func2)
        ok_(func4 != func3)
        ok_(func4 != func5)
        ok_(func4 != func6)
        ok_(func4 != func7)
        ok_(func5 != func1)
        ok_(func5 != func2)
        ok_(func5 != func3)
        ok_(func5 != func4)
        ok_(func5 != func6)
        ok_(func5 != func7)
        ok_(func6 != func1)
        ok_(func6 != func2)
        ok_(func6 != func3)
        ok_(func6 != func4)
        ok_(func6 != func5)
        ok_(func6 != func7)
        ok_(func7 != func1)
        ok_(func7 != func2)
        ok_(func7 != func4)
        ok_(func7 != func5)
        ok_(func7 != func6)
    
    def test_string(self):
        func = PermissiveFunction("perm", "foo", u"bár")
        eq_(unicode(func), u"perm(arg0=foo, oarg0=bár, oarg1=1)")
        eq_(str(func), "perm(arg0=foo, oarg0=b\xc3\xa1r, oarg1=1)")


class TestTruthOperator(object):
    """Tests for the :class:`TruthOperator`."""
    
    def test_constructor_with_boolean_operand(self):
        traffic_light = TrafficLightVar("traffic-light")
        TruthOperator(traffic_light)
    
    @raises(InvalidOperationError)
    def test_constructor_with_non_boolean_operand(self):
        # Constants cannot act as booleans
        constant = String("Paris")
        TruthOperator(constant)
    
    def test_evaluation(self):
        # Setup:
        traffic_light = TrafficLightVar("traffic-light")
        operation = TruthOperator(traffic_light)
        # Evaluation:
        ok_(operation( **dict(traffic_light="green") ))
        assert_false(operation( **dict(traffic_light="") ))
    
    def test_equivalence(self):
        """
        Two truth operations are equivalent if they evaluate the same operand.
        
        """
        op1 = TruthOperator(BoolVar())
        op2 = TruthOperator(BoolVar())
        op3 = TruthOperator(PedestriansCrossingRoad())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string(self):
        op = TruthOperator(BoolVar())
        as_unicode = unicode(op)
        eq_(as_unicode, "TruthOperator(Variable bool)")
        eq_(as_unicode, str(op))


class TestNotOperator(object):
    """Tests for the :class:`NotOperator`."""
    
    def test_constructor_with_boolean_operand(self):
        traffic_light = TrafficLightVar("traffic-light")
        NotOperator(traffic_light)
    
    def test_constructor_with_operator(self):
        """The Not operator must also support operators as operands"""
        traffic_light = TrafficLightVar("traffic-light")
        NotOperator(TruthOperator(traffic_light))
    
    @raises(InvalidOperationError)
    def test_constructor_with_non_boolean_operand(self):
        # Constants cannot act as booleans
        constant = String("Paris")
        NotOperator(constant)
    
    def test_evaluation(self):
        # Setup:
        traffic_light = TrafficLightVar("traffic-light")
        operation = NotOperator(traffic_light)
        # Evaluation:
        ok_(operation( **dict(traffic_light="") ))
        assert_false(operation( **dict(traffic_light="green") ))
    
    def test_equivalent(self):
        """
        Two negation operations are equivalent if they evaluate the same 
        operand.
        
        """
        op1 = NotOperator(BoolVar())
        op2 = NotOperator(BoolVar())
        op3 = NotOperator(PedestriansCrossingRoad())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string(self):
        op1 = NotOperator(BoolVar())
        op2 = NotOperator(AndOperator(BoolVar(), BoolVar()))
        as_unicode1 = unicode(op1)
        as_unicode2 = unicode(op2)
        eq_(as_unicode1, "NotOperator(Variable bool)")
        eq_(as_unicode1, str(op1))
        eq_(as_unicode2,
            "NotOperator(AndOperator(Variable bool, Variable bool))")
        eq_(as_unicode2, str(op2))


class TestAndOperator(object):
    """Tests for the And operator."""
    
    def test_constructor_with_operands(self):
        """The constructor must support actual operands as arguments"""
        AndOperator(BoolVar(), TrafficLightVar("traffic-light"))
    
    def test_constructor_with_operators(self):
        """The constructor must support operators as arguments."""
        AndOperator(
            NotOperator(BoolVar()),
            NotOperator(TrafficLightVar("traffic-light"))
        )
    
    def test_constructor_with_mixed_operands(self):
        """
        The constructor must support operators and actual operands as arguments.
        
        """
        AndOperator(BoolVar(), NotOperator(TrafficLightVar("traffic-light")))
        AndOperator(NotOperator(BoolVar()), TrafficLightVar("traffic-light"))
    
    def test_with_both_results_as_true(self):
        operation = AndOperator(BoolVar(), TrafficLightVar("traffic-light"))
        ok_(operation( **dict(bool=True, traffic_light="red") ))
    
    def test_with_both_results_as_false(self):
        operation = AndOperator(BoolVar(), TrafficLightVar("traffic-light"))
        assert_false(operation( **dict(bool=False, traffic_light="") ))
    
    def test_with_mixed_results(self):
        operation = AndOperator(BoolVar(), TrafficLightVar("traffic-light"))
        assert_false(operation( **dict(bool=False, traffic_light="red") ))
    
    def test_evaluation_order(self):
        """
        For efficiency, the second operand must not be evaluated if the first
        one is False.
        
        """
        op1 = BoolVar()
        op2 = BoolVar()
        AndOperator(op1, op2)(bool=False)
        ok_(op1.evaluated)
        assert_false(op2.evaluated)
    
    def test_equivalent(self):
        """Two conjunctions are equivalent if they have the same operands."""
        op1 = AndOperator(BoolVar(), PedestriansCrossingRoad())
        op2 = AndOperator(PedestriansCrossingRoad(), BoolVar())
        op3 = AndOperator(DriversAwaitingGreenLightVar(), BoolVar())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string(self):
        op = AndOperator(BoolVar(), BoolVar())
        as_unicode = unicode(op)
        eq_(as_unicode, "AndOperator(Variable bool, Variable bool)")
        eq_(as_unicode, str(op))


class TestOrOperator(object):
    """Tests for the Or operator."""
    
    def test_constructor_with_operands(self):
        """The constructor must support actual operands as arguments"""
        OrOperator(BoolVar(), TrafficLightVar("traffic-light"))
    
    def test_constructor_with_operators(self):
        """The constructor must support operators as arguments."""
        OrOperator(
            NotOperator(BoolVar()),
            NotOperator(TrafficLightVar("traffic-light"))
        )
    
    def test_constructor_with_mixed_operands(self):
        """
        The constructor must support operators and actual operands as arguments.
        
        """
        OrOperator(BoolVar(), NotOperator(TrafficLightVar("traffic-light")))
        OrOperator(NotOperator(BoolVar()), TrafficLightVar("traffic-light"))
    
    def test_with_both_results_as_true(self):
        operation = OrOperator(BoolVar(), TrafficLightVar("traffic-light"))
        ok_(operation( **dict(bool=True, traffic_light="red") ))
    
    def test_with_both_results_as_false(self):
        operation = OrOperator(BoolVar(), TrafficLightVar("traffic-light"))
        assert_false(operation( **dict(bool=False, traffic_light="") ))
    
    def test_with_mixed_results(self):
        operation = OrOperator(BoolVar(), TrafficLightVar("traffic-light"))
        ok_(operation( **dict(bool=False, traffic_light="red") ))
    
    def test_evaluation_order(self):
        """
        For efficiency, the second operand must not be evaluated if the first
        one is True.
        
        """
        op1 = BoolVar()
        op2 = BoolVar()
        OrOperator(op1, op2)(bool=True)
        ok_(op1.evaluated)
        assert_false(op2.evaluated)
    
    def test_equivalent(self):
        """
        Two inclusive disjunctions are equivalent if they have the same
        operands.
        
        """
        op1 = OrOperator(BoolVar(), PedestriansCrossingRoad())
        op2 = OrOperator(PedestriansCrossingRoad(), BoolVar())
        op3 = OrOperator(DriversAwaitingGreenLightVar(), BoolVar())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string(self):
        op = OrOperator(BoolVar(), BoolVar())
        as_unicode = unicode(op)
        eq_(as_unicode, "OrOperator(Variable bool, Variable bool)")
        eq_(as_unicode, str(op))


class TestXorOperator(object):
    """Tests for the Xor operator."""
    
    def test_constructor_with_operands(self):
        """The constructor must support actual operands as arguments"""
        XorOperator(BoolVar(), TrafficLightVar("traffic-light"))
    
    def test_constructor_with_operators(self):
        """The constructor must support operators as arguments."""
        XorOperator(
            NotOperator(BoolVar()),
            NotOperator(TrafficLightVar("traffic-light"))
        )
    
    def test_constructor_with_mixed_operands(self):
        """
        The constructor must support operators and actual operands as arguments.
        
        """
        XorOperator(BoolVar(), NotOperator(TrafficLightVar("traffic-light")))
        XorOperator(NotOperator(BoolVar()), TrafficLightVar("traffic-light"))
    
    def test_with_both_results_as_true(self):
        operation = XorOperator(BoolVar(), TrafficLightVar("traffic-light"))
        assert_false(operation( **dict(bool=True, traffic_light="red") ))
    
    def test_with_both_results_as_false(self):
        operation = XorOperator(BoolVar(), TrafficLightVar("traffic-light"))
        assert_false(operation( **dict(bool=False, traffic_light="") ))
    
    def test_with_mixed_results(self):
        operation = XorOperator(BoolVar(), TrafficLightVar("traffic-light"))
        ok_(operation( **dict(bool=False, traffic_light="red") ))
    
    def test_equivalent(self):
        """
        Two exclusive disjunctions are equivalent if they have the same
        operands.
        
        """
        op1 = XorOperator(BoolVar(), PedestriansCrossingRoad())
        op2 = XorOperator(PedestriansCrossingRoad(), BoolVar())
        op3 = XorOperator(DriversAwaitingGreenLightVar(), BoolVar())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string(self):
        op = XorOperator(BoolVar(), BoolVar())
        as_unicode = unicode(op)
        eq_(as_unicode, "XorOperator(Variable bool, Variable bool)")
        eq_(as_unicode, str(op))


class TestNonConnectiveBinaryOperators(object):
    """
    Tests for non-connective, binary operators.
    
    This is, all the binary operators, excluding And, Or and Xor.
    
    For these tests, I'll use the equality operator to avoid importing the
    base :class:`BinaryOperator`.
    
    """
    
    def test_constructor_with_constants(self):
        """The order must not change when the parameters are constant."""
        l_op = String("hola")
        r_op = String("chao")
        operation = EqualOperator(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variables(self):
        """The order must not change when the parameters are variable."""
        l_op = BoolVar()
        r_op = BoolVar()
        operation = EqualOperator(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variable_before_constant(self):
        """
        The order must not change when the first argument is a variable and the
        other is a constant.
        
        """
        l_op = BoolVar()
        r_op = String("hello")
        operation = EqualOperator(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variable_before_constant(self):
        """
        The order must change when the first argument is a constant and the
        other is a variable.
        
        """
        l_op = String("hello")
        r_op = BoolVar()
        operation = EqualOperator(l_op, r_op)
        eq_(r_op, operation.master_operand)
        eq_(l_op, operation.slave_operand)
    
    def test_equivalent(self):
        """
        Two binary operators are equivalent if they have the same operands.
        
        """
        op1 = EqualOperator(BoolVar(), PedestriansCrossingRoad())
        op2 = EqualOperator(PedestriansCrossingRoad(), BoolVar())
        op3 = EqualOperator(DriversAwaitingGreenLightVar(), BoolVar())
        
        op1.check_equivalence(op2)
        op2.check_equivalence(op1)
        
        assert_raises(AssertionError, op1.check_equivalence, op3)
        assert_raises(AssertionError, op2.check_equivalence, op3)
        assert_raises(AssertionError, op3.check_equivalence, op1)
        assert_raises(AssertionError, op3.check_equivalence, op2)
        
        ok_(op1 == op2)
        ok_(op2 == op1)
        ok_(op1 != op3)
        ok_(op2 != op3)
        ok_(op3 != op1)
        ok_(op3 != op2)
    
    def test_string(self):
        op = EqualOperator(String(u"qué hora es?"), BoolVar())
        eq_(unicode(op), u'EqualOperator(Variable bool, "qué hora es?")')
        eq_(str(op), 'EqualOperator(Variable bool, "qu\xc3\xa9 hora es?")')


class TestEqualOperator():
    """Tests for the Equality operator."""
    
    def test_constants_evaluation(self):
        operation1 = EqualOperator(String("hola"), String("hola"))
        operation2 = EqualOperator(String("hola"), String("chao"))
        ok_(operation1())
        assert_false(operation2())
    
    def test_variables_evaluation(self):
        operation = EqualOperator(PedestriansCrossingRoad(),
                                     DriversAwaitingGreenLightVar())
        
        # The pedestrians awaiting the green light to cross the street are
        # the same drivers... Must be a parallel universe!
        helpers = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("carla", "gustavo")
        }
        ok_(operation(**helpers))
        
        # The pedestrians are different from the drivers... That's my universe!
        helpers = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("liliana", "carlos")
        }
        assert_false(operation(**helpers))
    
    def test_mixed_evaluation(self):
        operation = EqualOperator(
            PedestriansCrossingRoad(),
            Set(String("gustavo"), String("carla"))
        )
        
        # The same people:
        helpers = {'pedestrians_crossroad': ("gustavo", "carla")}
        ok_(operation(**helpers))
        
        # Other people:
        helpers = {'pedestrians_crossroad': ("liliana", "carlos")}
        assert_false(operation(**helpers))


class TestNotEqualOperator():
    """Tests for the "not equal" operator."""
    
    def test_constants_evaluation(self):
        operation1 = NotEqualOperator(String("hola"), String("chao"))
        operation2 = NotEqualOperator(String("hola"), String("hola"))
        ok_(operation1())
        assert_false(operation2())
    
    def test_variables_evaluation(self):
        operation = NotEqualOperator(PedestriansCrossingRoad(),
                                     DriversAwaitingGreenLightVar())
        
        # The pedestrians are different from the drivers... That's my universe!
        helpers = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("liliana", "carlos")
        }
        ok_(operation(**helpers))
        
        # The pedestrians awaiting the green light to cross the street are
        # the same drivers... Must be a parallel universe!
        helpers = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("carla", "gustavo")
        }
        assert_false(operation(**helpers))
    
    def test_mixed_evaluation(self):
        operation = NotEqualOperator(
            PedestriansCrossingRoad(),
            Set(String("gustavo"), String("carla"))
        )
        
        # Other people:
        helpers = {'pedestrians_crossroad': ("liliana", "carlos")}
        ok_(operation(**helpers))
        
        # The same people:
        helpers = {'pedestrians_crossroad': ("gustavo", "carla")}
        assert_false(operation(**helpers))


class TestInequalities(object):
    """
    Tests for common functionalities in the inequality operators.
    
    Because we shouldn't the base :class:`_InequalityOperator`, we're going to
    use one of its subclasses: LessThanOperator.
    
    """
    
    def test_constructor_with_constants(self):
        """The order must not change when the parameters are constant."""
        l_op = Number(3)
        r_op = Number(4)
        operation = LessThanOperator(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variables(self):
        """The order must not change when the parameters are variables."""
        l_op = PedestriansCrossingRoad()
        r_op = DriversAwaitingGreenLightVar()
        operation = LessThanOperator(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variable_before_constant(self):
        """
        The order must not change when the first parameter is a variable and
        the second is a constant.
        
        """
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = LessThanOperator(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)


class TestLessThanOperator(object):
    """Tests for the evaluation of "less than" operations."""
    
    def test_constructor_with_constant_before_variable(self):
        """
        The order *must* change when the first parameter is a constant and
        the second is a variable.
        
        """
        l_op = Number(2)
        r_op = PedestriansCrossingRoad()
        operation = LessThanOperator(l_op, r_op)
        eq_(r_op, operation.master_operand)
        eq_(l_op, operation.slave_operand)
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = LessThanOperator(l_op, r_op)
        assert_false(operation())
    
    def test_two_constants(self):
        l_op = Number(3)
        r_op = Number(4)
        operation = LessThanOperator(l_op, r_op)
        ok_(operation())
    
    def test_two_variables(self):
        l_op = PedestriansCrossingRoad()
        r_op = NumVar()
        operation = LessThanOperator(l_op, r_op)
        
        # |{"carla"}| < 2   <=>   1 < 2
        helpers = {
            'pedestrians_crossroad': ("carla", ),
            'num': 2,
        }
        ok_(operation(**helpers))
        
        # |{"carla", "carlos"}| < 1   <=>   2 < 1
        helpers = {
            'pedestrians_crossroad': ("carla", "carlos"),
            'num': 1,
        }
        assert_false(operation(**helpers))
    
    def test_mixed_arguments(self):
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = LessThanOperator(l_op, r_op)
        
        # |{"carla"}| < 2   <=>   1 < 2
        helpers = {'pedestrians_crossroad': ("carla", )}
        ok_(operation(**helpers))
        
        # |{"carla", "carlos", "liliana"}| < 2   <=>   3 < 2
        helpers = {'pedestrians_crossroad': ("carla", "carlos", "liliana")}
        assert_false(operation(**helpers))


class TestGreaterThanOperator(object):
    """Tests for the evaluation of "greater than" operations."""
    
    def test_constructor_with_constant_before_variable(self):
        """
        The order *must* change when the first parameter is a constant and
        the second is a variable.
        
        """
        l_op = Number(2)
        r_op = PedestriansCrossingRoad()
        operation = GreaterThanOperator(l_op, r_op)
        eq_(r_op, operation.master_operand)
        eq_(l_op, operation.slave_operand)
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = GreaterThanOperator(l_op, r_op)
        assert_false(operation())
    
    def test_two_constants(self):
        l_op = Number(4)
        r_op = Number(3)
        operation = GreaterThanOperator(l_op, r_op)
        ok_(operation())
    
    def test_two_variables(self):
        l_op = PedestriansCrossingRoad()
        r_op = NumVar()
        operation = GreaterThanOperator(l_op, r_op)
        
        # |{"carla", "yolmary"}| > 1   <=>   2 > 1
        helpers = {
            'pedestrians_crossroad': ("carla", "yolmary"),
            'num': 1,
        }
        ok_(operation(**helpers))
        
        # |{"carla", "carlos"}| > 3   <=>   2 > 3
        helpers = {
            'pedestrians_crossroad': ("carla", "carlos"),
            'num': 3,
        }
        assert_false(operation(**helpers))
    
    def test_mixed_arguments(self):
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = GreaterThanOperator(l_op, r_op)
        
        # |{"carla", "yolmary", "manuel"}| > 2   <=>   3 > 2
        helpers = {'pedestrians_crossroad': ("carla", "yolmary", "manuel")}
        ok_(operation(**helpers))
        
        # |{"carla"}| > 2   <=>   1 > 2
        helpers = {'pedestrians_crossroad': ("carla", )}
        assert_false(operation(**helpers))


class TestLessEqualOperator(object):
    """Tests for the evaluation of "less than or equal to" operations."""
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = LessEqualOperator(l_op, r_op)
        ok_(operation())
    
    def test_two_constants(self):
        l_op = Number(3)
        r_op = Number(4)
        operation = LessEqualOperator(l_op, r_op)
        ok_(operation())
    
    def test_two_variables(self):
        l_op = PedestriansCrossingRoad()
        r_op = NumVar()
        operation = LessEqualOperator(l_op, r_op)
        
        # |{"carla"}| < 2   <=>   1 < 2
        helpers = {
            'pedestrians_crossroad': ("carla", ),
            'num': 2,
        }
        ok_(operation(**helpers))
        
        # |{"carla", "carlos"}| < 1   <=>   2 < 1
        helpers = {
            'pedestrians_crossroad': ("carla", "carlos"),
            'num': 1,
        }
        assert_false(operation(**helpers))
    
    def test_mixed_arguments(self):
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = LessEqualOperator(l_op, r_op)
        
        # |{"carla"}| < 2   <=>   1 < 2
        helpers = {'pedestrians_crossroad': ("carla", )}
        ok_(operation(**helpers))
        
        # |{"carla", "carlos", "liliana"}| < 2   <=>   1 < 2
        helpers = {'pedestrians_crossroad': ("carla", "carlos", "liliana")}
        assert_false(operation(**helpers))


class TestGreaterEqualOperator(object):
    """Tests for the evaluation of "greater than or equal to" operations."""
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = GreaterEqualOperator(l_op, r_op)
        ok_(operation())
    
    def test_two_constants(self):
        l_op = Number(4)
        r_op = Number(3)
        operation = GreaterEqualOperator(l_op, r_op)
        ok_(operation())
    
    def test_two_variables(self):
        l_op = PedestriansCrossingRoad()
        r_op = NumVar()
        operation = GreaterEqualOperator(l_op, r_op)
        
        # |{"carla", "yolmary"}| > 1   <=>   2 > 1
        helpers = {
            'pedestrians_crossroad': ("carla", "yolmary"),
            'num': 1,
        }
        ok_(operation(**helpers))
        
        # |{"carla", "carlos"}| > 3   <=>   2 > 3
        helpers = {
            'pedestrians_crossroad': ("carla", "carlos"),
            'num': 3,
        }
        assert_false(operation(**helpers))
    
    def test_mixed_arguments(self):
        l_op = PedestriansCrossingRoad()
        r_op = Number(2)
        operation = GreaterEqualOperator(l_op, r_op)
        
        # |{"carla", "yolmary", "manuel"}| > 2   <=>   3 > 2
        helpers = {'pedestrians_crossroad': ("carla", "yolmary", "manuel")}
        ok_(operation(**helpers))
        
        # |{"carla"}| > 2   <=>   1 > 2
        helpers = {'pedestrians_crossroad': ("carla", )}
        assert_false(operation(**helpers))


class TestContainsOperator(object):
    """Tests for the ``∈`` set operator."""
    
    def test_item_and_set(self):
        item = Number(3)
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = ContainsOperator(item, set_)
        eq_(operation.master_operand, set_)
        eq_(operation.slave_operand, item)
    
    def test_item_and_non_set(self):
        item = String("Paris")
        set_ = String("France")
        assert_raises(InvalidOperationError, ContainsOperator, item, set_)
    
    def test_constant_evaluation(self):
        item = Number(3)
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = ContainsOperator(item, set_)
        ok_(operation())
    
    def test_variable_evaluation(self):
        item = NumVar()
        set_ = PedestriansCrossingRoad()
        operation = ContainsOperator(item, set_)
        
        # 4 ∈ {"madrid", 4}
        helpers = {
            'num': 4,
            'pedestrians_crossroad': ("madrid", 4)
        }
        ok_(operation(**helpers))
        
        # 4 ∈ {"madrid", "paris", "london"}
        helpers = {
            'num': 4,
            'pedestrians_crossroad': ("madrid", "paris", "london")
        }
        assert_false(operation(**helpers))


class TestSubsetOperator(object):
    """Tests for the ``⊂`` set operator."""
    
    def test_set_and_set(self):
        subset = Set(Number(2), Number(4))
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = SubsetOperator(subset, set_)
        eq_(operation.master_operand, set_)
        eq_(operation.slave_operand, subset)
    
    def test_non_set_and_non_set(self):
        subset = String("Paris")
        set_ = String("France")
        assert_raises(InvalidOperationError, SubsetOperator, subset, set_)
    
    def test_constant_evaluation(self):
        subset = Set(Number(3), Number(1), Number(7))
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = SubsetOperator(subset, set_)
        ok_(operation())
    
    def test_variable_evaluation(self):
        subset = DriversAwaitingGreenLightVar()
        set_ = PedestriansCrossingRoad()
        operation = SubsetOperator(subset, set_)
        
        # {"carla"} ⊂ {"carla", "andreina"}
        helpers = {
            'drivers_trafficlight': ("carla", ),
            'pedestrians_crossroad': ("andreina", "carla")
        }
        ok_(operation(**helpers))
        
        # {"liliana", "carlos"} ⊂ {"manuel", "yolmary", "carla"}
        helpers = {
            'drivers_trafficlight': ("liliana", "carlos"),
            'pedestrians_crossroad': ("manuel", "yolmary", "carla")
        }
        assert_false(operation(**helpers))


#{ Mock objects


class PermissiveFunction(FunctionOperator):
    """
    A mock function operator which accepts any type of arguments.
    
    """
    
    required_arguments = ("arg0", )
    
    optional_arguments = {'oarg0': None, 'oarg1': 1}
    
    def check_arguments(self):
        """Do nothing -- Allow any kind of arguments."""
        pass


class BoolVar(Variable):
    """
    Mock variable which represents the boolean value stored in a helper called
    ``bool``.
    
    """
    operations = set(("boolean", "equality"))
    
    required_helpers = ("bool", )
    
    def __init__(self, **names):
        self.evaluated = False
        super(BoolVar, self).__init__("bool", **names)
    
    def to_python(self, **helpers):
        """Return the value of the ``bool`` helper"""
        self.evaluated = True
        return helpers['bool']
    
    def equals(self, value, **helpers):
        """Does ``value`` equal this boolean variable?"""
        self.evaluated = True
        return helpers['bool'] == value
    
    def get_logical_value(self, **helpers):
        """Does the value of helper ``bool`` evaluate to True?"""
        self.evaluated = True
        return bool(helpers['bool'])


class NumVar(Variable):
    """
    Mock variable which represents a numeric value stored in a helper called
    ``num``.
    
    """
    
    operations = set(["equality", "inequality"])
    
    required_helpers = ("num", )
    
    def __init__(self, **names):
        super(NumVar, self).__init__("num", **names)
    
    def to_python(self, **helpers):
        return helpers['num']
    
    def equals(self, value, **helpers):
        return helpers['num'] == value
    
    def less_than(self, value, **helpers):
        return helpers['num'] < value
    
    def greater_than(self, value, **helpers):
        return helpers['num'] > value


#}

