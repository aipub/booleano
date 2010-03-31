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

