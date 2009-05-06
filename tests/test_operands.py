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
Tests for the operands.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises

from booleano.operations.operands import (Operand, String, Number, Set,
                                            Variable)
from booleano.exc import InvalidOperationError


class TestOperand(object):
    """
    Tests for the base class Operand.
    
    """
    
    def setUp(self):
        """Create an instance of Operand"""
        self.op = Operand()
    
    def test_supported_operations(self):
        """Operands shouldn't support any operation by default"""
        eq_(0, len(self.op.operations))
    
    def test_required_helpers(self):
        """Operands shouldn't require any helper by default"""
        eq_(0, len(self.op.required_helpers))
    
    def test_operation_methods(self):
        """No operation should be supported by default"""
        assert_raises(NotImplementedError, self.op.to_python)
        assert_raises(NotImplementedError, self.op.is_met)
        assert_raises(NotImplementedError, self.op.equals, None)
        assert_raises(NotImplementedError, self.op.greater_than, None)
        assert_raises(NotImplementedError, self.op.less_than, None)
        assert_raises(NotImplementedError, self.op.contains, None)
        assert_raises(NotImplementedError, self.op.is_subset, None)


class TestVariable(object):
    """Tests for variable operands."""
    
    def test_no_language_specific_names(self):
        greeting_var = Variable("greeting")
        eq_("greeting", greeting_var.global_name)
        eq_({}, greeting_var.names)
    
    def test_with_language_specific_names(self):
        """
        There are no language-specific names defined by default.
        
        """
        names = {
            'fr': "bonjour",
            'en': "hi",
            'es': "hello",
        }
        greeting_var = Variable("greeting", **names)
        eq_(names, greeting_var.names)
    
    def test_with_default_language_specific_names(self):
        """
        Variables can be created with default names in any language.
        
        """
        class GreetingVariable(Variable):
            default_names = {'fr': "bonjour"}
        
        # Appending names:
        greeting_var = GreetingVariable("greet", en="hi", es="hola")
        eq_({'fr': "bonjour", 'en': "hi", 'es': "hola"}, greeting_var.names)
        # Appending and replacing names:
        greeting_var = GreetingVariable("greet", fr="salut", es="hola")
        eq_({'fr': "salut", 'es': "hola"}, greeting_var.names)


#{ Constants tests


class TestString(object):
    """
    Tests for :class:`String` contants.
    
    """
    
    def test_operations(self):
        """String constants must only support equality operations"""
        eq_(String.operations, set(["equality"]))
    
    def test_python_value(self):
        op = String("carabobo")
        eq_(op.to_python(), "carabobo")
    
    def test_equality(self):
        op = String("freedomware")
        ok_(op.equals("freedomware"))
        assert_false(op.equals(" freedomware "))
        assert_false(op.equals("microsoftware"))
    
    def test_number_support(self):
        """Strings given as a number must be converted first into a string"""
        # When the constant is defined as a number:
        op = String(10)
        ok_(op.equals("10"))
        # When the constant is defined as a string:
        op = String("10")
        ok_(op.equals(10))
        # When both are defined as numbers:
        op = String(10)
        ok_(op.equals(10))


class TestNumber(object):
    """
    Tests for :class:`Number` constants.
    
    """
    
    def test_operations(self):
        """
        Numeric constants must only support equality and inequality operations.
        
        """
        eq_(Number.operations, set(["equality", "inequality"]))
    
    def test_python_value(self):
        op = Number(22)
        eq_(op.to_python(), 22.00)
    
    def test_equality_with_integer_constant(self):
        # With an integer constant:
        op = Number(10)
        ok_(op.equals(10))
        ok_(op.equals(10.00))
        assert_false(op.equals(9.99999))
        assert_false(op.equals(10.00001))
        # With a float constant:
        op = Number(10.00)
        ok_(op.equals(10))
        ok_(op.equals(10.00))
        assert_false(op.equals(9.99999))
        assert_false(op.equals(10.00001))
        # Checking an invalid comparison:
        assert_raises(InvalidOperationError, op.equals, "today")
    
    def test_greater_than(self):
        # With an integer constant:
        op = Number(10)
        ok_(op.greater_than(9))
        ok_(op.greater_than(9.99999))
        assert_false(op.greater_than(10.00001))
        # With a float constant:
        op = Number(10.00)
        ok_(op.greater_than(9))
        ok_(op.greater_than(9.99999))
        assert_false(op.greater_than(10.00001))
    
    def test_less_than(self):
        # With an integer constant:
        op = Number(10)
        ok_(op.less_than(11))
        ok_(op.less_than(10.00001))
        assert_false(op.less_than(9.99999))
        # With a float constant:
        op = Number(10.00)
        ok_(op.less_than(11))
        ok_(op.less_than(10.00001))
        assert_false(op.less_than(9.99999))
    
    def test_string_support(self):
        """Numbers given as strings must be converted first"""
        # The constant as a string:
        op = Number("10")
        ok_(op.equals(10))
        ok_(op.equals(10.00))
        # The other operand as string:
        op = Number(10)
        ok_(op.equals("10"))
        ok_(op.equals("10.00"))
        ok_(op.less_than("11"))
        ok_(op.greater_than("9"))
        assert_false(op.less_than("9"))
        assert_false(op.greater_than("11"))


class TestSet(object):
    """
    Tests for :class:`Set` constants.
    
    """
    
    def test_operations(self):
        """
        Constant sets must only support equality, inequality and membership
        operations.
        
        """
        eq_(Set.operations, set(["equality", "inequality", "membership"]))
    
    def test_python_value(self):
        op = Set(Number(10), Number(1), String("paola"))
        eq_(op.to_python(), set((10, 1, "paola")))
    
    def test_instantiation(self):
        """All the members of a set must be operands"""
        # Instantiation with operands:
        Set(Number(3), String("hola"))
        # Instantiation with a non-operand value:
        try:
            Set(Number(3), "hola")
            assert False, "InvalidOperationError exception not raised"
        except InvalidOperationError, exc:
            assert 'Item "hola" is not an operand' in unicode(exc)
    
    def test_equality(self):
        op = Set(Number(3), String("hola"))
        set1 = set([3, "hola"])
        set2 = set([3])
        set3 = set([3, "hola", "something else"])
        set4 = set(["nothing to do"])
        # Comparing them...
        ok_(op.equals(set1), "The constant equals %s" % op.constant_value)
        assert_false(op.equals(set2))
        assert_false(op.equals(set3))
        assert_false(op.equals(set4))
    
    def test_less_than(self):
        op = Set(String("carla"), String("andreina"), String("liliana"))
        ok_(op.less_than(4))
        ok_(op.less_than("4"))
        assert_false(op.less_than(2))
        assert_false(op.less_than(1))
        assert_raises(InvalidOperationError, op.less_than, "some string")
        assert_raises(InvalidOperationError, op.less_than, 3.10)
    
    def test_greater_than(self):
        op = Set(String("carla"), String("andreina"), String("liliana"))
        ok_(op.greater_than(2))
        ok_(op.greater_than("2"))
        assert_false(op.greater_than(3))
        assert_false(op.greater_than(4))
        assert_raises(InvalidOperationError, op.greater_than, "some string")
        assert_raises(InvalidOperationError, op.greater_than, 2.60)
    
    def test_contains(self):
        op = Set(String("arepa"), Number(4))
        ok_(op.contains(4))
        ok_(op.contains(4.00))
        ok_(op.contains("arepa"))
        assert_false(op.contains("something else"))
    
    def test_subset(self):
        op = Set(String("carla"), String("andreina"), String("liliana"))
        ok_(op.is_subset(["carla"]))
        ok_(op.is_subset(["carla", "liliana"]))
        ok_(op.is_subset(["andreina", "carla"]))
        assert_false(op.is_subset(["gustavo", "carlos"]))
        assert_false(op.is_subset(["carla", "gustavo"]))


#}
