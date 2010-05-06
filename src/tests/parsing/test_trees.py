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
Tests for the parse trees.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises

from booleano.parser.trees import EvaluableParseTree, ConvertibleParseTree
from booleano.nodes.operations import And
from booleano.nodes.constants import String, PlaceholderVariable
from booleano.exc import InvalidOperationError

from tests.utils.mock_converters import AntiConverter
from tests.utils.mock_nodes import (TrafficLightVar,
    PedestriansCrossingRoad, BoolVar, DriversAwaitingGreenLightVar)


class TestEvaluableTrees(object):
    """Tests for the truth-evaluable trees."""
    
    def test_operand(self):
        """Operands alone can valid evaluable parse trees."""
        operand = TrafficLightVar()
        tree = EvaluableParseTree(operand)
        # True
        context = {'traffic_light': "red"}
        ok_(tree(context))
        # False
        context = {'traffic_light': None}
        assert_false(tree(context))
    
    def test_non_boolean_operands(self):
        """Only operands that support logical values are supported."""
        operand = String("I'm a string")
        assert_raises(InvalidOperationError, EvaluableParseTree, operand)
    
    def test_operation(self):
        """Operations are valid evaluable parse trees."""
        operation = And(PedestriansCrossingRoad(),
                        DriversAwaitingGreenLightVar())
        tree = EvaluableParseTree(operation)
        # True
        context = {'pedestrians_crossroad': ("gustavo", "carla"),
                   'drivers_trafficlight': ("andreina", "juan")}
        ok_(tree(context))
        # False
        context = {'pedestrians_crossroad': (),
                   'drivers_traffic_light': ()}
        assert_false(tree(context))
    
    def test_equivalence(self):
        tree1 = EvaluableParseTree(BoolVar())
        tree2 = EvaluableParseTree(BoolVar())
        tree3 = EvaluableParseTree(PedestriansCrossingRoad())
        tree4 = ConvertibleParseTree(PlaceholderVariable("my_variable"))
        
        ok_(tree1 == tree2)
        ok_(tree2 == tree1)
        
        ok_(tree1 != None)
        ok_(tree1 != tree3)
        ok_(tree1 != tree4)
        ok_(tree2 != tree3)
        ok_(tree2 != tree4)
        ok_(tree3 != tree1)
        ok_(tree3 != tree2)
        ok_(tree3 != tree4)
        ok_(tree4 != tree1)
        ok_(tree4 != tree2)
        ok_(tree4 != tree3)
    
    def test_string(self):
        tree = EvaluableParseTree(BoolVar())
        as_unicode = unicode(tree)
        expected = "Evaluable parse tree (Anonymous variable [BoolVar])"
        eq_(as_unicode, expected)
    
    def test_representation(self):
        tree = EvaluableParseTree(BoolVar())
        expected = "<Parse tree (evaluable) <Anonymous variable [BoolVar]>>"
        eq_(repr(tree), expected)


class TestConvertibleTrees(object):
    """Tests for the convertible trees."""
    
    def test_operands(self):
        """Operands alone are valid convertible parse trees."""
        operand = PlaceholderVariable("my_variable", None)
        tree = ConvertibleParseTree(operand)
        converter = AntiConverter()
        conversion = tree(converter)
        eq_(operand, conversion)
    
    def test_equivalence(self):
        tree1 = ConvertibleParseTree(PlaceholderVariable("my_variable"))
        tree2 = ConvertibleParseTree(PlaceholderVariable("my_variable"))
        tree3 = ConvertibleParseTree(String("hello"))
        tree4 = EvaluableParseTree(BoolVar())
        
        ok_(tree1 == tree2)
        ok_(tree2 == tree1)
        
        ok_(tree1 != None)
        ok_(tree1 != tree3)
        ok_(tree1 != tree4)
        ok_(tree2 != tree3)
        ok_(tree2 != tree4)
        ok_(tree3 != tree1)
        ok_(tree3 != tree2)
        ok_(tree3 != tree4)
        ok_(tree4 != tree1)
        ok_(tree4 != tree2)
        ok_(tree4 != tree3)
    
    def test_string(self):
        tree = ConvertibleParseTree(BoolVar())
        as_unicode = unicode(tree)
        expected = "Convertible parse tree (Anonymous variable [BoolVar])"
        eq_(as_unicode, expected)
    
    def test_representation(self):
        tree = ConvertibleParseTree(BoolVar())
        expected = "<Parse tree (convertible) " \
                   "<Anonymous variable [BoolVar]>>"
        eq_(repr(tree), expected)

