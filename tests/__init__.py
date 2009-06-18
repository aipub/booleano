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
Test suite for Booleano.

This module contains utilities shared among the whole test suite.

"""

from booleano.converters import BaseConverter
from booleano.operations import (Truth, Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, Contains, IsSubset,
    String, Number, Set, Variable, Function, VariablePlaceholder,
    FunctionPlaceholder)
from booleano.exc import InvalidOperationError, BadCallError


#{ Mock variables


class TrafficLightVar(Variable):
    """
    Variable that represents a traffic light.
    
    """
    
    operations = set(("equality", "boolean"))
    
    required_helpers = ("traffic_light", )
    
    valid_colors = ("red", "amber", "green")
    
    def to_python(self, **helpers):
        """Return the string that represents the current light color"""
        return helpers['traffic_light']
    
    def get_logical_value(self, **helpers):
        """Is the traffic light working?"""
        return bool(helpers['traffic_light'])
    
    def equals(self, value, **helpers):
        """Does the traffic light's color equal to ``value``?"""
        if value not in self.valid_colors:
            raise InvalidOperationError("Traffic lights can't be %s" % value)
        return value == helpers['traffic_light']


class VariableSet(Variable):
    """
    Base class for a variable which finds its value in one of the helpers.
    
    Descendants have to define the helper that contains the set, in
    the ``required_helpers`` attribute (it must not require more than one
    helper).
    
    """
    
    operations = set(("equality", "inequality", "boolean", "membership"))
    
    def to_python(self, **helpers):
        set_ = set(helpers[self.required_helpers[0]])
        return set_
    
    def get_logical_value(self, **helpers):
        set_ = set(helpers[self.required_helpers[0]])
        return bool(set_)
    
    def equals(self, value, **helpers):
        set_ = set(helpers[self.required_helpers[0]])
        value = set(value)
        return value == set_
    
    def less_than(self, value, **helpers):
        set_ = helpers[self.required_helpers[0]]
        return len(set_) < value
    
    def greater_than(self, value, **helpers):
        set_ = helpers[self.required_helpers[0]]
        return len(set_) > value
    
    def contains(self, value, **helpers):
        set_ = helpers[self.required_helpers[0]]
        return value in set_
    
    def is_subset(self, value, **helpers):
        value = set(value)
        set_ = set(helpers[self.required_helpers[0]])
        return value.issubset(set_)


class PedestriansCrossingRoad(VariableSet):
    """Variable that represents the pedestrians crossing the street."""
    
    required_helpers = ["pedestrians_crossroad"]


class DriversAwaitingGreenLightVar(VariableSet):
    """
    Variable that represents the drivers waiting for the green light to
    cross the crossroad.
    
    """
    
    required_helpers = ["drivers_trafficlight"]


#{ Mock functions


class PermissiveFunction(Function):
    """
    A mock function operator which accepts any type of arguments.
    
    """
    
    operations = set(["boolean"])
    
    required_arguments = ("arg0", )
    
    optional_arguments = {'oarg0': Set(), 'oarg1': Number(1)}
    
    def check_arguments(self):
        """Do nothing -- Allow any kind of arguments."""
        pass
    
    def to_python(self, **helpers):
        return self.arguments
    
    def get_logical_value(self, **helpers):
        return True


class TrafficViolationFunc(Function):
    """
    Function operator that checks if there are drivers/pedestrians crossing
    the crossroad when their respective traffic light is red.
    
    """
    
    operations = set(["boolean"])
    
    required_arguments = ("light", )
    
    def check_arguments(self):
        assert isinstance(self.arguments['light'], String)
        light = self.arguments['light'].constant_value
        if light not in ("pedestrians", "drivers"):
            raise BadCallError("Only pedestrians and drivers have lights")
    
    def to_python(self, **helpers):
        return self.arguments
    
    def get_logical_value(self, **helpers):
        if self.arguments['light'] == "pedestrians":
            return helpers['pedestrians_light'] == "red" and \
                   len(helpers['people_crossing'])
        # It's the drivers' light.
        return helpers['drivers_light'] == "red" and \
               len(helpers['cars_crossing'])


#{ Miscellaneous stuff


class AntiConverter(BaseConverter):
    """
    A parse tree converter that returns the original parse tree.
    
    This is the simplest way to check the converter.
    
    """
    
    def convert_truth(self, operand):
        return Truth(operand)
    
    def convert_not(self, operand):
        return Not(operand)
    
    def convert_and(self, master_operand, slave_operand):
        return And(master_operand, slave_operand)
    
    def convert_or(self, master_operand, slave_operand):
        return Or(master_operand, slave_operand)
    
    def convert_xor(self, master_operand, slave_operand):
        return Xor(master_operand, slave_operand)
    
    def convert_equal(self, master_operand, slave_operand):
        return Equal(master_operand, slave_operand)
    
    def convert_not_equal(self, master_operand, slave_operand):
        return NotEqual(master_operand, slave_operand)
    
    def convert_less_than(self, master_operand, slave_operand):
        return LessThan(master_operand, slave_operand)
    
    def convert_greater_than(self, master_operand, slave_operand):
        return GreaterThan(master_operand, slave_operand)
    
    def convert_less_equal(self, master_operand, slave_operand):
        return LessEqual(master_operand, slave_operand)
    
    def convert_greater_equal(self, master_operand, slave_operand):
        return GreaterEqual(master_operand, slave_operand)
    
    def convert_contains(self, master_operand, slave_operand):
        return Contains(slave_operand, master_operand,)
    
    def convert_is_subset(self, master_operand, slave_operand):
        return IsSubset(slave_operand, master_operand)
    
    def convert_string(self, operand):
        return String(operand)
    
    def convert_number(self, operand):
        return Number(operand)
    
    def convert_set(self, *operands):
        return Set(*operands)
    
    def convert_variable(self, name):
        return VariablePlaceholder(name)
    
    def convert_function(self, name, *arguments):
        return FunctionPlaceholder(name, *arguments)


#}
