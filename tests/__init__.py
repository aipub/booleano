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
    
    def is_met(self, **helpers):
        """Is the traffic light working?"""
        return bool(helpers['traffic_light'])
    
    def equals(self, value, **helpers):
        """Does the traffic light's color equal to ``value``?"""
        value = value.lower()
        if value not in self.valid_colors:
            raise InvalidOperationError('Traffic lights cannot be in %s' % value)
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
    
    def is_met(self, **helpers):
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
        set_ = set(helpers[self.required_helpers[0]])
        return set_.issubset(value)


class PedestriansCrossingRoad(VariableSet):
    """Variable that represents the pedestrians crossing the street."""
    
    required_helpers = ["pedestrians_crossroad"]


class DriversAwaitingGreenLightVar(Variable):
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
    
    required_arguments = ("traffic_light", "people_crossing")
    
    def __call__(self, **helpers):
        if helpers['traffic_light'] == "red" and \
           len(helpers['people_crossing']):
            return True
        return False

#}
