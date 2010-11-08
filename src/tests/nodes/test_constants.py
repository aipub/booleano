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
Tests for unbounded operands.

"""

from nose.tools import eq_, ok_, assert_false

from booleano.exc import InvalidOperationError
from booleano.nodes.datatypes import NumberType, SetType, StringType
from booleano.nodes.constants import Constant, String, Number, Set


#{ Constants


class TestConstant(object):
    """Tests for the base :class:`Constant`."""
    
    def test_equality(self):
        """
        Two constants are equivalents if they represent the same Python constant
        value.
        
        """
        shared_value = object()
        constant1 = MockConstant(shared_value)
        constant2 = MockConstant(object())
        constant3 = MockConstant(shared_value)
        
        ok_(constant1 == constant1)
        assert_false(constant1 == constant2)
        ok_(constant1 == constant3)
        assert_false(constant2 == constant1)
        ok_(constant2 == constant2)
        assert_false(constant2 == constant3)
        ok_(constant3 == constant1)
        assert_false(constant3 == constant2)
        ok_(constant3 == constant3)
    
    def test_hash(self):
        """
        The hash of a constant is the hash of the Python value it represents.
        
        """
        value = object()
        constant = MockConstant(value)
        eq_(hash(value), hash(constant))


class TestString(object):
    """
    Tests for :class:`String` contants.
    
    """
    
    def test_node_type(self):
        """Strings are leaf nodes and implement the String datatype."""
        string = String("greeting")
        ok_(string.is_leaf)
        ok_(isinstance(string, StringType))
    
    def test_python_strings(self):
        """Constant strings represent Python :class:`unicode` objects."""
        ascii_text = String("tomorrow!")
        unicode_text = String(u"¡mañana!")
        
        py_ascii_text = ascii_text.get_as_string(None)
        py_unicode_text = unicode_text.get_as_string(None)
        
        ok_(isinstance(py_ascii_text, unicode))
        ok_(isinstance(py_unicode_text, unicode))
        
        eq_(py_ascii_text, u"tomorrow!")
        eq_(py_unicode_text, u"¡mañana!")
    
    def test_equivalence(self):
        """
        Two constant strings are equivalent if they represent the same string.
        
        """
        text1 = String("hello world")
        text2 = String("hello earth")
        text3 = String("hello world")
        
        ok_(text1 == text1)
        assert_false(text1 == text2)
        ok_(text1 == text3)
        assert_false(text2 == text1)
        ok_(text2 == text2)
        assert_false(text2 == text3)
        ok_(text3 == text1)
        assert_false(text3 == text2)
        ok_(text3 == text3)
    
    def test_representation(self):
        # With Unicode:
        string = String(u"caña")
        eq_(repr(string), '<String "caña">')
        # With ASCII
        string = String("cana")
        eq_(repr(string), '<String "cana">')


class TestNumber(object):
    """
    Tests for :class:`Number` constants.
    
    """
    
    def test_node_type(self):
        """Numbers are leaf nodes and implement the Number datatype."""
        number = Number(4)
        ok_(number.is_leaf)
        ok_(isinstance(number, NumberType))
    
    def test_python_numbers(self):
        """Constant numbers represent Python :class:`float` objects."""
        integer_number = Number(4)
        float_number = Number(2.5)
        
        py_integer_number = integer_number.get_as_number(None)
        py_float_number = float_number.get_as_number(None)
        
        ok_(isinstance(py_integer_number, float))
        ok_(isinstance(py_float_number, float))
        eq_(py_integer_number, 4.0)
        eq_(py_float_number, 2.5)
    
    def test_equivalence(self):
        """
        Two constant numbers are equivalent if they represent the same number.
        
        """
        number1 = Number(22)
        number2 = Number(23)
        number3 = Number(22)
        
        ok_(number1 == number1)
        assert_false(number1 == number2)
        ok_(number1 == number3)
        assert_false(number2 == number1)
        ok_(number2 == number2)
        assert_false(number2 == number3)
        ok_(number3 == number1)
        assert_false(number3 == number2)
        ok_(number3 == number3)
    
    def test_representation(self):
        number = Number(4)
        eq_(repr(number), "<Number 4.0>")


class TestSet(object):
    """
    Tests for :class:`Set` constants.
    
    """
    
    def test_node_type(self):
        """Sets are branch nodes and implement the Set datatype."""
        set_ = Set(String("arg0"))
        assert_false(set_.is_leaf)
        ok_(isinstance(set_, SetType))
    
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
    
    def test_equivalence(self):
        """
        Two constant sets A and B are equivalent if they have the same
        cardinality and each element in A is equivalent to one element in B.
        
        """
        set1 = Set(String("hi"), Set(Number(3), String("hello")))
        set2 = Set(String("hi"), Number(3), String("hello"))
        set3 = Set(Set(String("hello"), Number(3)), String("hi"))
        set4 = Set(String("hi"), String("hello"))
        
        ok_(set1 == set1)
        assert_false(set1 == set2)
        ok_(set1 == set3)
        assert_false(set1 == set4)
        assert_false(set2 == set1)
        ok_(set2 == set2)
        assert_false(set2 == set3)
        assert_false(set2 == set4)
        ok_(set3 == set1)
        assert_false(set3 == set2)
        ok_(set3 == set3)
        assert_false(set3 == set4)
        assert_false(set4 == set1)
        assert_false(set4 == set2)
        assert_false(set4 == set3)
        ok_(set4 == set4)
    
    def test_representation(self):
        set1 = Set(Number(3), Number(5))
        eq_(repr(set1), "<Set <Number 3.0>, <Number 5.0>>")
        # Now with an empty set:
        set2 = Set()
        eq_(repr(set2), "<Set>")
        # Now with Unicode stuff in it:
        set3 = Set(String(u"España"), String(u"carabobeño"))
        eq_(repr(set3), '<Set <String "España">, <String "carabobeño">>')


#{ Test utilities


class MockConstant(Constant):
    """
    Mock constant which only implements abstract members.
    
    """
    
    is_leaf = True
    
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._constant_value)


#}
