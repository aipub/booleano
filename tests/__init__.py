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

from booleano.operations.operators import FunctionOperator
from booleano.operations.operands import Variable
from booleano.exc import InvalidOperationError


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
    
    def __init__(self, **names):
        super(VariableSet, self).__init__(self.required_helpers[0], **names)
    
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


#{ Mock function operators


class TrafficViolationFunc(FunctionOperator):
    """
    Function operator that checks if there are drivers/pedestrians crossing
    the crossroad when their respective traffic light is red.
    
    """
    
    required_arguments = ("light", )
    
    def check_arguments(self):
        if self.arguments['light'] not in ("pedestrians", "drivers"):
            raise BadCallError("Only pedestrians and drivers have lights")
    
    def __call__(self, **helpers):
        if self.arguments['light'] == "pedestrians":
            return helpers['pedestrians_light'] == "red" and \
                   len(helpers['people_crossing'])
        # It's the drivers' light.
        return helpers['drivers_light'] == "red" and \
               len(helpers['cars_crossing'])

#}
