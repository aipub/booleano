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
Test suite for the datatypes.

We basically want to test abstract functionality.

"""
from nose.tools import eq_, ok_, assert_false, assert_raises

from booleano.nodes.datatypes import (Datatype, BooleanType, NumberType,
                                      StringType, SetType)


class TestDatatypeFiltering(object):
    """
    Tests to ensure the meta-class of the Booleano datatypes filters the base
    classes which are datatypes.
    
    """
    
    def test_pre_set_datatypes(self):
        """Pre-set Booleano datatypes are respected."""
        
        preset_types = ("foo", "bar")
        
        class FooType(Datatype):
            __booleano_base_types__ = preset_types
        
        eq_(FooType.__booleano_base_types__, preset_types)
    
    #{ Datatypes whose bases are all datatypes
    
    def test_primitive_type(self):
        """Classes with no bases (apart from ``object``) have no datatypes."""
        class FooType(Datatype): pass
        
        eq_(len(FooType.__booleano_base_types__), 0)
    
    def test_one_base_type(self):
        """Types with one base primitive type implement only one type."""
        class FooType(PrimitiveType1): pass
        
        eq_(len(FooType.__booleano_base_types__), 1)
        eq_(FooType.__booleano_base_types__[0], PrimitiveType1)
    
    def test_one_single_derived_base_type(self):
        """
        Types derived from another type which extends a primitive implement
        two types: The parent and their grandparent.
        
        """
        class FooType(SingleDerivedType1): pass
        
        eq_(len(FooType.__booleano_base_types__), 2)
        eq_(FooType.__booleano_base_types__[0], SingleDerivedType1)
        eq_(FooType.__booleano_base_types__[1], PrimitiveType1)
    
    def test_one_composite_derived_base_type(self):
        """
        Types derived from another type which extend two primitives implement
        three types: The parent and their two granparents.
        
        """
        class FooType(CompositeDerivedType): pass
        
        eq_(len(FooType.__booleano_base_types__), 3)
        eq_(FooType.__booleano_base_types__[0], CompositeDerivedType)
        eq_(FooType.__booleano_base_types__[1], PrimitiveType1)
        eq_(FooType.__booleano_base_types__[2], PrimitiveType2)
    
    def test_one_third_generation_base_type(self):
        """
        Types derived from a 3rd generation type implement four types: The
        parent, their granparent and their grand-grandparent.
        
        """
        class FooType(GrandchildType): pass
        
        eq_(len(FooType.__booleano_base_types__), 3)
        eq_(FooType.__booleano_base_types__[0], GrandchildType)
        eq_(FooType.__booleano_base_types__[1], SingleDerivedType1)
        eq_(FooType.__booleano_base_types__[2], PrimitiveType1)
    
    def test_two_base_primitive_types(self):
        """Types with two base primitive types implement only two types."""
        class FooType(PrimitiveType1, PrimitiveType2): pass
        
        eq_(len(FooType.__booleano_base_types__), 2)
        eq_(FooType.__booleano_base_types__[0], PrimitiveType1)
        eq_(FooType.__booleano_base_types__[1], PrimitiveType2)
    
    def test_two_base_compound_types(self):
        """Types with two base compound types implement four types."""
        class FooType(SingleDerivedType1, SingleDerivedType2): pass
        
        eq_(len(FooType.__booleano_base_types__), 4)
        eq_(FooType.__booleano_base_types__[0], SingleDerivedType1)
        eq_(FooType.__booleano_base_types__[1], PrimitiveType1)
        eq_(FooType.__booleano_base_types__[2], SingleDerivedType2)
        eq_(FooType.__booleano_base_types__[3], PrimitiveType2)
    
    def test_two_base_compound_types_with_diamon(self):
        """
        Types with two base compound types implement all their ancestor types,
        minus any common base among the two parents.
        
        """
        # PrimitiveType1 is a common base in SingleDerivedType1 and
        # CompositeDerivedType:
        class FooType(SingleDerivedType1, CompositeDerivedType): pass
        class BazType(CompositeDerivedType, SingleDerivedType1): pass
        
        eq_(len(FooType.__booleano_base_types__), 4)
        eq_(FooType.__booleano_base_types__[0], SingleDerivedType1)
        eq_(FooType.__booleano_base_types__[1], CompositeDerivedType)
        eq_(FooType.__booleano_base_types__[2], PrimitiveType1)
        eq_(FooType.__booleano_base_types__[3], PrimitiveType2)
        
        eq_(len(BazType.__booleano_base_types__), 4)
        eq_(BazType.__booleano_base_types__[0], CompositeDerivedType)
        eq_(BazType.__booleano_base_types__[1], SingleDerivedType1)
        eq_(BazType.__booleano_base_types__[2], PrimitiveType1)
        eq_(BazType.__booleano_base_types__[3], PrimitiveType2)
    
    #{ Datatypes whose bases are Booleano datatypes and other Python classes
    
    def test_leading_non_types(self):
        """
        The first base classes which are not Booleano datatypes are not taken
        as part of the base types for that datatype.
        
        """
        # One leading non-datatype class:
        class FooType(MockClass1, PrimitiveType1): pass
        eq_(len(FooType.__booleano_base_types__), 1)
        eq_(FooType.__booleano_base_types__[0], PrimitiveType1)
        
        # Two leading non-datatype classes:
        class BazType(MockClass1, MockClass2, PrimitiveType1): pass
        eq_(len(BazType.__booleano_base_types__), 1)
        eq_(BazType.__booleano_base_types__[0], PrimitiveType1)
    
    def test_trailing_non_types(self):
        """
        The last base classes which are not Booleano datatypes are not taken
        as part of the base types for that datatype.
        
        """
        # One trailing non-datatype class:
        class FooType(PrimitiveType1, MockClass1): pass
        eq_(len(FooType.__booleano_base_types__), 1)
        eq_(FooType.__booleano_base_types__[0], PrimitiveType1)
        
        # Two trailing non-datatype classes:
        class BazType(PrimitiveType1, MockClass1, MockClass2): pass
        eq_(len(BazType.__booleano_base_types__), 1)
        eq_(BazType.__booleano_base_types__[0], PrimitiveType1)
    
    def test_in_between_non_types(self):
        """
        Base classes which are not Booleano datatypes but are surrounded by them
        are not taken as part of the base types for that datatype.
        
        Only the base datatype classes are taken.
        
        """
        # One non-datatype class in between two primitives:
        class FooType(PrimitiveType1, MockClass1, PrimitiveType2): pass
        eq_(len(FooType.__booleano_base_types__), 2)
        eq_(FooType.__booleano_base_types__[0], PrimitiveType1)
        eq_(FooType.__booleano_base_types__[1], PrimitiveType2)
        
        # Two non-datatype classes in between two primitives:
        class BazType(PrimitiveType1, MockClass1, MockClass2, PrimitiveType2):
            pass
        eq_(len(BazType.__booleano_base_types__), 2)
        eq_(BazType.__booleano_base_types__[0], PrimitiveType1)
        eq_(BazType.__booleano_base_types__[1], PrimitiveType2)
        
        # One non-datatype class in between a derived type and a primitive:
        class BarType(SingleDerivedType1, MockClass1, PrimitiveType2): pass
        eq_(len(BarType.__booleano_base_types__), 3)
        eq_(BarType.__booleano_base_types__[0], SingleDerivedType1)
        eq_(BarType.__booleano_base_types__[1], PrimitiveType1)
        eq_(BarType.__booleano_base_types__[2], PrimitiveType2)
    
    #}


def test_inheritance():
    """All the datatypes are descendant of Datatype."""
    ok_(issubclass(BooleanType, Datatype))
    ok_(issubclass(NumberType, Datatype))
    ok_(issubclass(StringType, Datatype))
    ok_(issubclass(SetType, Datatype))


def test_instantiation():
    """Datatypes cannot be instantiated directly -- they're all abstract."""
    assert_raises(TypeError, BooleanType)
    assert_raises(TypeError, NumberType)
    assert_raises(TypeError, StringType)
    assert_raises(TypeError, SetType)


def test_boolean_callable():
    """Booleans can be called directly to get the logical value."""
    positive_bool = MockBoolean(True)
    negative_bool = MockBoolean(False)
    ok_(positive_bool(None))
    assert_false(negative_bool(None))


#{ Test utilities


class MockBoolean(BooleanType):
    
    def __init__(self, result):
        self.result = result
    
    def get_as_boolean(self, context):
        return self.result


class MockClass1(object):
    """Mock Python class which is not a Booleano datatype."""
    pass


class MockClass2(object):
    """Another mock Python class which is not a Booleano datatype."""
    pass


class PrimitiveType1(Datatype):
    """Mock Booleano datatype."""
    pass


class PrimitiveType2(Datatype):
    """Another mock Booleano datatype."""
    pass


class SingleDerivedType1(PrimitiveType1):
    """Mock Booleano type which implements a primitive type."""
    pass


class SingleDerivedType2(PrimitiveType2):
    """Another mock Booleano type which implements a primitive type."""
    pass


class CompositeDerivedType(PrimitiveType1, PrimitiveType2):
    """Mock Booleano type which implements two primitive types."""
    pass


class GrandchildType(SingleDerivedType1):
    """Mock Booleano type which implements a type derived from a primitive."""
    pass


#}
