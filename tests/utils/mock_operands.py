# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://booleano.efous.org/>.
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
Mock operands.

"""
from booleano.nodes.operands import String, Number, Set, Variable, Function
from booleano.exc import InvalidOperationError, BadCallError


#{ Mock variables


class BoolVar(Variable):
    """
    Mock variable which represents the boolean value stored in a context item
    called ``bool``.
    
    """
    operations = set(("boolean", "equality"))
    
    def __init__(self):
        self.evaluated = False
        super(BoolVar, self).__init__()
    
    def to_python(self, context):
        """Return the value of the ``bool`` context item"""
        self.evaluated = True
        return context['bool']
    
    def equals(self, value, context):
        """Does ``value`` equal this boolean variable?"""
        self.evaluated = True
        return context['bool'] == value
    
    def __call__(self, context):
        """Does the value of context item ``bool`` evaluate to True?"""
        self.evaluated = True
        return bool(context['bool'])


class TrafficLightVar(Variable):
    """
    Variable that represents a traffic light.
    
    """
    
    operations = set(("equality", "boolean"))
    
    valid_colors = ("red", "amber", "green")
    
    def to_python(self, context):
        """Return the string that represents the current light color"""
        return context['traffic_light']
    
    def __call__(self, context):
        """Is the traffic light working?"""
        return bool(context['traffic_light'])
    
    def equals(self, value, context):
        """Does the traffic light's color equal to ``value``?"""
        if value not in self.valid_colors:
            raise InvalidOperationError("Traffic lights can't be %s" % value)
        return value == context['traffic_light']


class VariableSet(Variable):
    """
    Base class for a variable which finds its value in one of the context.
    
    Descendants have to define the context item that contains the set, in
    the ``people_set`` attribute.
    
    """
    
    operations = set(("equality", "inequality", "boolean", "membership"))
    
    def to_python(self, context):
        set_ = set(context[self.people_set])
        return set_
    
    def __call__(self, context):
        set_ = set(context[self.people_set])
        return bool(set_)
    
    def equals(self, value, context):
        set_ = set(context[self.people_set])
        value = set(value)
        return value == set_
    
    def less_than(self, value, context):
        set_ = context[self.people_set]
        return len(set_) < value
    
    def greater_than(self, value, context):
        set_ = context[self.people_set]
        return len(set_) > value
    
    def belongs_to(self, value, context):
        set_ = context[self.people_set]
        return value in set_
    
    def is_subset(self, value, context):
        value = set(value)
        set_ = set(context[self.people_set])
        return value.issubset(set_)


class PedestriansCrossingRoad(VariableSet):
    """Variable that represents the pedestrians crossing the street."""
    
    people_set = "pedestrians_crossroad"


class DriversAwaitingGreenLightVar(VariableSet):
    """
    Variable that represents the drivers waiting for the green light to
    cross the crossroad.
    
    """
    
    people_set = "drivers_trafficlight"


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
    
    def to_python(self, context):
        return self.arguments
    
    def __call__(self, context):
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
    
    def to_python(self, context):
        return self.arguments
    
    def __call__(self, context):
        if self.arguments['light'] == "pedestrians":
            return context['pedestrians_light'] == "red" and \
                   len(context['people_crossing'])
        # It's the drivers' light.
        return context['drivers_light'] == "red" and \
               len(context['cars_crossing'])

