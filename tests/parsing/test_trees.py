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
Tests for the parse trees.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises, raises

from booleano.parser.trees import EvaluableParseTree, ConvertibleParseTree
from booleano.operations import And, String, VariablePlaceholder
from booleano.exc import InvalidOperationError

from tests import (TrafficLightVar, PedestriansCrossingRoad, BoolVar,
                   DriversAwaitingGreenLightVar, AntiConverter)


class TestEvaluableTrees(object):
    """Tests for the truth-evaluable trees."""
    
    def test_operand(self):
        """Operands alone can valid evaluable parse trees."""
        operand = TrafficLightVar()
        tree = EvaluableParseTree(operand)
        # True
        helpers = {'traffic_light': "red"}
        ok_(tree(**helpers))
        # False
        helpers = {'traffic_light': None}
        assert_false(tree(**helpers))
    
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
        helpers = {'pedestrians_crossroad': ("gustavo", "carla"),
                   'drivers_trafficlight': ("andreina", "juan")}
        ok_(tree(**helpers))
        # False
        helpers = {'pedestrians_crossroad': (),
                   'drivers_traffic_light': ()}
        assert_false(tree(**helpers))
    
    def test_string(self):
        tree = EvaluableParseTree(BoolVar())
        as_unicode = unicode(tree)
        expected = "Evaluable parse tree (Truth(Anonymous variable [BoolVar]))"
        eq_(as_unicode, expected)
    
    def test_representation(self):
        tree = EvaluableParseTree(BoolVar())
        expected = "<Parse tree (evaluable) <Truth " \
                   "<Anonymous variable [BoolVar]>>>"
        eq_(repr(tree), expected)


class TestConvertibleTrees(object):
    """Tests for the convertible trees."""
    
    def test_operands(self):
        """Operands alone are valid convertible parse trees."""
        operand = VariablePlaceholder("my_variable", None)
        tree = ConvertibleParseTree(operand)
        converter = AntiConverter()
        conversion = tree(converter)
        eq_(operand, conversion)
    
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

