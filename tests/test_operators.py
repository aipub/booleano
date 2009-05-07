# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 by Gustavo Narea <http://gustavonarea.net/>
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>
#
# Booleano is freedomware: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# Booleano is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Booleano. If not, see <http://www.gnu.org/licenses/>.

"""
Tests for the operands.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises, raises

from booleano.operations.operators import *
from booleano.operations.operands import String, Number, Set, Variable
from booleano.exc import InvalidOperationError, BadCallError, BadFunctionError

from tests import (TrafficLightVar, PedestriansCrossingRoad,
                   DriversAwaitingGreenLightVar)


class TestFunctions(object):
    """Tests for the base class of user-defined function operators."""
    
    def test_constructor_with_minimum_arguments(self):
        func = PermissiveFunction("this-is-arg0")
        args = {
            'arg0': "this-is-arg0",
            'oarg0': None,
            'oarg1': 1
        }
        eq_(func.arguments, args)
    
    def test_constructor_with_one_optional_argument(self):
        func = PermissiveFunction("this-is-arg0", "this-is-oarg0")
        args = {
            'arg0': "this-is-arg0",
            'oarg0': "this-is-oarg0",
            'oarg1': 1
        }
        eq_(func.arguments, args)
    
    def test_constructor_with_all_arguments(self):
        func = PermissiveFunction("this-is-arg0", "this-is-oarg0",
                                  "this-is-oarg1")
        args = {
            'arg0': "this-is-arg0",
            'oarg0': "this-is-oarg0",
            'oarg1': "this-is-oarg1"
        }
        eq_(func.arguments, args)
    
    @raises(BadCallError)
    def test_constructor_with_few_arguments(self):
        PermissiveFunction()
    
    @raises(BadCallError)
    def test_constructor_with_many_arguments(self):
        PermissiveFunction(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    
    def test_no_validation_by_default(self):
        """
        Arguments must be explicitly validated by the function.
        
        This is, their .check_arguments() method must be overriden.
        
        """
        class MockFunction(FunctionOperator): pass
        assert_raises(NotImplementedError, MockFunction)
    
    def test_evaluation_not_implemented(self):
        """Expression evaluation must *not* be available by default"""
        class FakeFunction(FunctionOperator):
            def check_arguments(self):
                pass
        
        func = FakeFunction()
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


class TestNonConnectiveBinaryOperators(object):
    """
    Tests for non-connective, binary operators.
    
    This is, all the binary operators, excluding And, Or and Xor.
    
    For these tests, I'll use the equality operator to avoid importing the
    base "Operator" class.
    
    """
    
    def test_constructor_with_constants(self):
        """The order must not change when the parameters are constant."""
        l_op = String("hola")
        r_op = String("chao")
        operation = EqualityOperator(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variables(self):
        """The order must not change when the parameters are variable."""
        l_op = BoolVar()
        r_op = BoolVar()
        operation = EqualityOperator(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variable_before_constant(self):
        """
        The order must not change when the first argument is a variable and the
        other is a constant.
        
        """
        l_op = BoolVar()
        r_op = String("hello")
        operation = EqualityOperator(l_op, r_op)
        eq_(l_op, operation.master_operand)
        eq_(r_op, operation.slave_operand)
    
    def test_constructor_with_variable_before_constant(self):
        """
        The order must change when the first argument is a constant and the
        other is a variable.
        
        """
        l_op = String("hello")
        r_op = BoolVar()
        operation = EqualityOperator(l_op, r_op)
        eq_(r_op, operation.master_operand)
        eq_(l_op, operation.slave_operand)


class TestEqualityOperator():
    """Tests for the Equality operator."""
    
    def test_constants_evaluation(self):
        operation1 = EqualityOperator(String("hola"), String("hola"))
        operation2 = EqualityOperator(String("hola"), String("chao"))
        ok_(operation1())
        assert_false(operation2())
    
    def test_variables_evaluation(self):
        operation = EqualityOperator(PedestriansCrossingRoad(),
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
        operation = EqualityOperator(
            PedestriansCrossingRoad(),
            Set(String("gustavo"), String("carla"))
        )
        
        # The same people:
        helpers = {'pedestrians_crossroad': ("gustavo", "carla")}
        ok_(operation(**helpers))
        
        # Other people:
        helpers = {'pedestrians_crossroad': ("liliana", "carlos")}
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
    
    def is_met(self, **helpers):
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

