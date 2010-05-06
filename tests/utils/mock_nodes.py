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
Mock operation nodes.

"""

from booleano.exc import BadCallError
from booleano.nodes import Function, OperationNode
from booleano.nodes.datatypes import BooleanType, SetType, StringType
from booleano.nodes.operands import String


__all__ = ["BranchNode", "BoolVar", "DriversAwaitingGreenLightVar", "LeafNode",
           "PedestriansCrossingRoad", "PermissiveFunction", "TrafficLightVar",
           "TrafficViolationFunc", "VariableSet"]


class MockNodeBase(OperationNode):
    """Base class for mock nodes."""
    
    def __init__(self, value=None):
        self.value = value
        super(MockNodeBase, self).__init__()
    
    def __eq__(self, other):
        equals = False
        if super(MockNodeBase, self).__eq__(other):
            equals = self.value == other.value
        return equals
    
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)


class LeafNode(MockNodeBase):
    """Mock leaf node."""
    is_leaf = True


class BranchNode(MockNodeBase):
    """Mock branch node."""
    is_leaf = False


#{ Mock variables


class BoolVar(OperationNode, BooleanType):
    """
    Mock variable which represents the boolean value stored in a context item
    called ``bool``.
    
    """
    
    def __init__(self):
        self.evaluated = False
        super(BoolVar, self).__init__()
    
    def get_as_boolean(self, context):
        """Return the value of the ``bool`` context item"""
        self.evaluated = True
        return context['bool']


class TrafficLightVar(OperationNode, BooleanType, StringType):
    """
    Variable that represents a traffic light.
    
    """
    
    valid_colors = ("red", "amber", "green")
    
    def get_as_string(self, context):
        """Return the string that represents the current light color"""
        return context['traffic_light']
    
    def get_as_boolean(self, context):
        """Is the traffic light working?"""
        return bool(context['traffic_light'])


class VariableSet(OperationNode, BooleanType, SetType):
    """
    Base class for a variable which finds its value in one of the context.
    
    Descendants have to define the context item that contains the set, in
    the ``people_set`` attribute.
    
    """
    
    def get_as_boolean(self, context):
        return bool(context[self.people_set])
    
    def get_as_number(self, value, context):
        return len(context[self.people_set])
    
    def get_as_set(self, context):
        set_ = set(context[self.people_set])
        return set_


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


class PermissiveFunction(Function, BooleanType):
    """
    A mock function operator which accepts any type of arguments.
    
    """
    
    required_arguments = ("arg0", )
    
    optional_arguments = {'oarg0': LeafNode("foo"), 'oarg1': BranchNode("bar")}
    
    def check_arguments(self):
        """Do nothing -- Allow any kind of arguments."""
        pass
    
    def get_as_boolean(self, context):
        return True
    
    def __eq__(self, other):
        return super(PermissiveFunction, self).__eq__(other)


class TrafficViolationFunc(Function, BooleanType):
    """
    Function operator that checks if there are drivers/pedestrians crossing
    the crossroad when their respective traffic light is red.
    
    """
    
    required_arguments = ("light", )
    
    def check_arguments(self):
        assert isinstance(self.arguments['light'], String)
        light = self.arguments['light'].constant_value
        if light not in ("pedestrians", "drivers"):
            raise BadCallError("Only pedestrians and drivers have lights")
    
    def get_as_boolean(self, context):
        if self.arguments['light'] == "pedestrians":
            return context['pedestrians_light'] == "red" and \
                   len(context['people_crossing'])
        # It's the drivers' light.
        return context['drivers_light'] == "red" and \
               len(context['cars_crossing'])
    
    def __eq__(self, other):
        return super(PermissiveFunction, self).__eq__(other)

