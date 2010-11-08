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
Tests for the operators.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises

from booleano.nodes.operations import (Not, And, Or, Xor, Equal,
    NotEqual, LessThan, GreaterThan, LessEqual, GreaterEqual, BelongsTo,
    IsSubset)
from booleano.nodes.constants import String, Number, Set
from booleano.nodes.datatypes import BooleanType
from booleano.exc import  InvalidOperationError

from tests.nodes import assert_node_equivalence
from tests.utils.mock_nodes import (BoolVar, DriversAwaitingGreenLightVar,
    NumVar, PedestriansCrossingRoad, TrafficLightVar)


class TestNot(object):
    """Tests for the :class:`Not`."""
    
    def test_argument_datatype(self):
        """The operand for Not must be a boolean."""
        eq_(Not.argument_types, BooleanType)
    
    def test_evaluation(self):
        # Setup:
        traffic_light = TrafficLightVar()
        operation = Not(traffic_light)
        # Evaluation:
        ok_(operation.get_as_boolean(dict(traffic_light="")))
        assert_false(operation.get_as_boolean(dict(traffic_light="green")))


class TestAnd(object):
    """Tests for the And operator."""
    
    def test_argument_datatype(self):
        """The operands must be both boolean."""
        eq_(And.argument_types, BooleanType)
    
    def test_with_both_results_as_true(self):
        operation = And(BoolVar(), TrafficLightVar())
        ok_(operation(dict(bool=True, traffic_light="red")))
    
    def test_with_both_results_as_false(self):
        operation = And(BoolVar(), TrafficLightVar())
        assert_false(operation(dict(bool=False, traffic_light="")))
    
    def test_with_mixed_results(self):
        operation = And(BoolVar(), TrafficLightVar())
        assert_false(operation(dict(bool=False, traffic_light="red")))
    
    def test_evaluation_order(self):
        """
        For efficiency, the second operand must not be evaluated if the first
        one returns False.
        
        """
        op1 = BoolVar()
        op2 = BoolVar()
        context = {'bool': False}
        And(op1, op2)(context)
        ok_(op1.evaluated)
        assert_false(op2.evaluated)
    
    def test_equivalence(self):
        """Two conjunctions are equivalent if they have the same operands."""
        op1 = And(BoolVar(), TrafficLightVar())
        op2 = And(TrafficLightVar(), BoolVar())
        op3 = And(DriversAwaitingGreenLightVar(), BoolVar())
        op4 = And(DriversAwaitingGreenLightVar(), BoolVar())
        op5 = Or(DriversAwaitingGreenLightVar(), BoolVar())
        
        assert_node_equivalence(
            (op1, op2),
            (op3, op4),
            (op5, ),
            )


class TestOr(object):
    """Tests for the Or operator."""
    
    def test_argument_datatype(self):
        """The operands must be both boolean."""
        eq_(Or.argument_types, BooleanType)
    
    def test_with_both_results_as_true(self):
        operation = Or(BoolVar(), TrafficLightVar())
        ok_(operation( dict(bool=True, traffic_light="red") ))
    
    def test_with_both_results_as_false(self):
        operation = Or(BoolVar(), TrafficLightVar())
        assert_false(operation( dict(bool=False, traffic_light="") ))
    
    def test_with_mixed_results(self):
        operation = Or(BoolVar(), TrafficLightVar())
        ok_(operation( dict(bool=False, traffic_light="red") ))
    
    def test_evaluation_order(self):
        """
        For efficiency, the second operand must not be evaluated if the first
        one is True.
        
        """
        op1 = BoolVar()
        op2 = BoolVar()
        context = {'bool': True}
        Or(op1, op2)(context)
        ok_(op1.evaluated)
        assert_false(op2.evaluated)
    
    def test_equivalence(self):
        """
        Two inclusive disjunctions are equivalent if they have the same
        operands.
        
        """
        op1 = Or(BoolVar(), PedestriansCrossingRoad())
        op2 = Or(PedestriansCrossingRoad(), BoolVar())
        op3 = Or(DriversAwaitingGreenLightVar(), BoolVar())
        op4 = Or(DriversAwaitingGreenLightVar(), BoolVar())
        op5 = And(DriversAwaitingGreenLightVar(), BoolVar())
        
        assert_node_equivalence(
            (op1, op2),
            (op3, op4),
            (op5, ),
            )


class TestXor(object):
    """Tests for the Xor operator."""
    
    def test_argument_datatype(self):
        """The operands must be both boolean."""
        eq_(Xor.argument_types, BooleanType)
    
    def test_with_both_results_as_true(self):
        operation = Xor(BoolVar(), TrafficLightVar())
        assert_false(operation( dict(bool=True, traffic_light="red") ))
    
    def test_with_both_results_as_false(self):
        operation = Xor(BoolVar(), TrafficLightVar())
        assert_false(operation( dict(bool=False, traffic_light="") ))
    
    def test_with_mixed_results(self):
        operation = Xor(BoolVar(), TrafficLightVar())
        ok_(operation( dict(bool=False, traffic_light="red") ))
    
    def test_equivalence(self):
        """
        Two exclusive disjunctions are equivalent if they have the same
        operands.
        
        """
        op1 = Xor(BoolVar(), PedestriansCrossingRoad())
        op2 = Xor(PedestriansCrossingRoad(), BoolVar())
        op3 = Xor(DriversAwaitingGreenLightVar(), BoolVar())
        op4 = Xor(DriversAwaitingGreenLightVar(), BoolVar())
        op5 = Or(DriversAwaitingGreenLightVar(), BoolVar())
        
        assert_node_equivalence(
            (op1, op2),
            (op3, op4),
            (op5, ),
            )


class TestEqual(object):
    """Tests for the Equality operator."""
    
    def test_constants_evaluation(self):
        operation1 = Equal(String("hola"), String("hola"))
        operation2 = Equal(String("hola"), String("chao"))
        ok_(operation1(None))
        assert_false(operation2(None))
    
    def test_variables_evaluation(self):
        operation = Equal(PedestriansCrossingRoad(),
                          DriversAwaitingGreenLightVar())
        
        # The pedestrians awaiting the green light to cross the street are
        # the same drivers... Must be a parallel universe!
        context = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("carla", "gustavo")
            }
        ok_(operation(context))
        
        # The pedestrians are different from the drivers... That's my universe!
        context = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("liliana", "carlos")
            }
        assert_false(operation(context))
    
    def test_mixed_evaluation(self):
        operation = Equal(
            PedestriansCrossingRoad(),
            Set(String("gustavo"), String("carla"))
            )
        
        # The same people:
        context = {'pedestrians_crossroad': ("gustavo", "carla")}
        ok_(operation(context))
        
        # Other people:
        context = {'pedestrians_crossroad': ("liliana", "carlos")}
        assert_false(operation(context))


class TestNotEqual(object):
    """Tests for the "not equal" operator."""
    
    def test_constants_evaluation(self):
        operation1 = NotEqual(String("hola"), String("chao"))
        operation2 = NotEqual(String("hola"), String("hola"))
        ok_(operation1(None))
        assert_false(operation2(None))
    
    def test_variables_evaluation(self):
        operation = NotEqual(PedestriansCrossingRoad(),
                                     DriversAwaitingGreenLightVar())
        
        # The pedestrians are different from the drivers... That's my universe!
        context = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("liliana", "carlos")
            }
        ok_(operation(context))
        
        # The pedestrians awaiting the green light to cross the street are
        # the same drivers... Must be a parallel universe!
        context = {
            'pedestrians_crossroad': ("gustavo", "carla"),
            'drivers_trafficlight': ("carla", "gustavo")
            }
        assert_false(operation(context))
    
    def test_mixed_evaluation(self):
        operation = NotEqual(
            PedestriansCrossingRoad(),
            Set(String("gustavo"), String("carla"))
            )
        
        # Other people:
        context = {'pedestrians_crossroad': ("liliana", "carlos")}
        ok_(operation(context))
        
        # The same people:
        context = {'pedestrians_crossroad': ("gustavo", "carla")}
        assert_false(operation(context))


class TestLessThan(object):
    """Tests for the evaluation of "less than" operations."""
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = LessThan(l_op, r_op)
        assert_false(operation(None))
    
    def test_left_less_than_right(self):
        l_op = Number(1)
        r_op = NumVar()
        operation = LessThan(l_op, r_op)
        
        context = {'num': 2}
        ok_(operation(context))
    
    def test_left_greater_than_right(self):
        l_op = Number(3)
        r_op = NumVar()
        operation = LessThan(l_op, r_op)
        
        context = {'num': 2}
        assert_false(operation(context))


class TestGreaterThan(object):
    """Tests for the evaluation of "greater than" operations."""
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = GreaterThan(l_op, r_op)
        assert_false(operation(None))
    
    def test_left_less_than_right(self):
        l_op = Number(1)
        r_op = NumVar()
        operation = GreaterThan(l_op, r_op)
        
        context = {'num': 2}
        assert_false(operation(context))
    
    def test_left_greater_than_right(self):
        l_op = Number(3)
        r_op = NumVar()
        operation = GreaterThan(l_op, r_op)
        
        context = {'num': 2}
        ok_(operation(context))


class TestLessEqual(object):
    """Tests for the evaluation of "less than or equal to" operations."""
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = LessEqual(l_op, r_op)
        ok_(operation(None))
    
    def test_left_less_than_right(self):
        l_op = Number(1)
        r_op = NumVar()
        operation = LessEqual(l_op, r_op)
        
        context = {'num': 2}
        ok_(operation(context))
    
    def test_left_greater_than_right(self):
        l_op = Number(3)
        r_op = NumVar()
        operation = LessEqual(l_op, r_op)
        
        context = {'num': 2}
        assert_false(operation(context))


class TestGreaterEqual(object):
    """Tests for the evaluation of "greater than or equal to" operations."""
    
    def test_identical_values(self):
        l_op = Number(3)
        r_op = Number(3)
        operation = GreaterEqual(l_op, r_op)
        ok_(operation(None))
    
    def test_left_less_than_right(self):
        l_op = Number(1)
        r_op = NumVar()
        operation = GreaterEqual(l_op, r_op)
        
        context = {'num': 2}
        assert_false(operation(context))
    
    def test_left_greater_than_right(self):
        l_op = Number(3)
        r_op = NumVar()
        operation = GreaterEqual(l_op, r_op)
        
        context = {'num': 2}
        ok_(operation(context))


class TestBelongsTo(object):
    """Tests for the ``∈`` set operator."""
    
    def test_item_and_set(self):
        item = Number(3)
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = BelongsTo(item, set_)
        eq_(operation.master_operand, set_)
        eq_(operation.slave_operand, item)
    
    def test_item_and_non_set(self):
        item = String("Paris")
        set_ = String("France")
        assert_raises(InvalidOperationError, BelongsTo, item, set_)
    
    def test_constant_evaluation(self):
        item = Number(3)
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = BelongsTo(item, set_)
        ok_(operation(None))
    
    def test_variable_evaluation(self):
        item = NumVar()
        set_ = PedestriansCrossingRoad()
        operation = BelongsTo(item, set_)
        
        # 4 ∈ {"madrid", 4}
        context = {
            'num': 4,
            'pedestrians_crossroad': ("madrid", 4)
            }
        ok_(operation(context))
        
        # 4 ∈ {"madrid", "paris", "london"}
        context = {
            'num': 4,
            'pedestrians_crossroad': ("madrid", "paris", "london")
            }
        assert_false(operation(context))


class TestIsSubset(object):
    """Tests for the ``⊂`` set operator."""
    
    def test_set_and_set(self):
        subset = Set(Number(2), Number(4))
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = IsSubset(subset, set_)
        eq_(operation.master_operand, set_)
        eq_(operation.slave_operand, subset)
    
    def test_constant_evaluation(self):
        subset = Set(Number(3), Number(1), Number(7))
        set_ = Set(Number(1), Number(3), Number(5), Number(7), Number(11))
        operation = IsSubset(subset, set_)
        ok_(operation(None))
    
    def test_variable_evaluation(self):
        subset = DriversAwaitingGreenLightVar()
        set_ = PedestriansCrossingRoad()
        operation = IsSubset(subset, set_)
        
        # {"carla"} ⊂ {"carla", "andreina"}
        context1 = {
            'drivers_trafficlight': ("carla", ),
            'pedestrians_crossroad': ("andreina", "carla")
            }
        ok_(operation(context1))
        
        # {"liliana", "carlos"} ⊂ {"manuel", "yolmary", "carla"}
        context2 = {
            'drivers_trafficlight': ("liliana", "carlos"),
            'pedestrians_crossroad': ("manuel", "yolmary", "carla")
            }
        assert_false(operation(context2))

