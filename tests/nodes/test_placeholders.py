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
Test for placeholder nodes.

"""
from nose.tools import eq_, ok_, assert_false, assert_raises

from booleano.exc import BadCallError
from booleano.nodes.operands import String, Number
from booleano.nodes.placeholders import PlaceholderVariable, PlaceholderFunction


class TestPlaceholderVariable(object):
    """Tests for the PlaceholderVariable."""
    
    def test_node_type(self):
        """Placeholder variables are leaf nodes."""
        var = PlaceholderVariable("greeting", None)
        ok_(var.is_leaf)
    
    def test_constructor(self):
        """
        Placeholder variables should contain an attribute which represents the
        name of the variable in question.
        
        """
        var1 = PlaceholderVariable(u"PAÍS", None)
        var2 = PlaceholderVariable("country", None)
        
        eq_(var1.name, u"país")
        eq_(var2.name, "country")
    
    def test_no_namespace(self):
        """Placeholder variables shouldn't have a default namespace."""
        var = PlaceholderVariable("foo")
        eq_(len(var.namespace_parts), 0)
    
    def test_namespace(self):
        """Placeholder variables should be aware of their namespace."""
        var = PlaceholderVariable("country", ("geo", "bar"))
        eq_(var.namespace_parts, ("geo", "bar"))
    
    def test_namespace_as_non_tuple(self):
        """Namespace parts must be stored as tuple."""
        var = PlaceholderVariable("country", ["geo", "bar"])
        eq_(var.namespace_parts, ("geo", "bar"))
    
    def test_equivalence(self):
        """
        Two placeholder variables are equivalent if they have the same name
        and share the same namespace.
        
        """
        var1 = PlaceholderVariable("foo", None)
        var2 = PlaceholderVariable("bar", None)
        var3 = PlaceholderVariable("Foo", None)
        var4 = PlaceholderVariable("foo", ["some", "namespace"])
        var5 = PlaceholderVariable("bar", ["some", "namespace"])
        var6 = PlaceholderVariable("foo", ["some", "namespace"])
        
        ok_(var1 == var1)
        assert_false(var1 == var2)
        ok_(var1 == var3)
        assert_false(var1 == var4)
        assert_false(var1 == var5)
        assert_false(var1 == var6)
        assert_false(var2 == var1)
        ok_(var2 == var2)
        assert_false(var2 == var3)
        assert_false(var2 == var4)
        assert_false(var2 == var5)
        assert_false(var2 == var6)
        ok_(var3 == var1)
        assert_false(var3 == var2)
        ok_(var3 == var3)
        assert_false(var3 == var4)
        assert_false(var3 == var5)
        assert_false(var3 == var6)
        assert_false(var4 == var1)
        assert_false(var4 == var2)
        assert_false(var4 == var3)
        ok_(var4 == var4)
        assert_false(var4 == var5)
        ok_(var4 == var6)
        assert_false(var5 == var1)
        assert_false(var5 == var2)
        assert_false(var5 == var3)
        assert_false(var5 == var4)
        ok_(var5 == var5)
        assert_false(var5 == var6)
        assert_false(var6 == var1)
        assert_false(var6 == var2)
        assert_false(var6 == var3)
        ok_(var6 == var4)
        assert_false(var6 == var5)
        ok_(var6 == var6)
    
    def test_representation_without_namespace(self):
        # With Unicode
        var = PlaceholderVariable(u"aquí", None)
        eq_(repr(var), '<Placeholder variable "aquí">')
        # With ASCII
        var = PlaceholderVariable("here", None)
        eq_(repr(var), '<Placeholder variable "here">')
    
    def test_representation_with_namespace(self):
        # With Unicode
        var = PlaceholderVariable(u"aquí", ["some", "thing"])
        eq_('<Placeholder variable "aquí" at namespace="some:thing">',
            repr(var))
        # With ASCII
        var = PlaceholderVariable("here", ["some", "thing"])
        eq_('<Placeholder variable "here" at namespace="some:thing">',
            repr(var))


class TestPlaceholderFunction(object):
    """Tests for the PlaceholderFunction."""
    
    def test_node_type(self):
        """Placeholder functions are branch nodes."""
        func = PlaceholderFunction("greet", None, String("arg0"))
        assert_false(func.is_leaf)
    
    def test_constructor(self):
        """
        Placeholder functions should contain an attribute which represents the
        name of the function in question and another one which represents the
        arguments passed.
        
        """
        func1 = PlaceholderFunction(u"PAÍS", None)
        eq_(func1.name, u"país")
        eq_(func1.arguments, ())
        
        func2 = PlaceholderFunction("country", None,
                                    PlaceholderFunction("city", None),
                                    Number(2))
        eq_(func2.name, "country")
        eq_(func2.arguments, (PlaceholderFunction("city", None), Number(2)))
    
    def test_no_namespace(self):
        """Placeholder functions shouldn't have a default namespace."""
        func = PlaceholderFunction("foo")
        eq_(len(func.namespace_parts), 0)
    
    def test_namespaces(self):
        """Placeholder functions should be aware of their namespace."""
        func = PlaceholderFunction("country", ("geo", "bar"))
        eq_(func.namespace_parts, ("geo", "bar"))
    
    def test_namespace_as_non_tuple(self):
        """Namespace parts must be stored as tuple."""
        func = PlaceholderFunction("country", ["geo", "bar"])
        eq_(func.namespace_parts, ("geo", "bar"))
    
    def test_non_operands_as_arguments(self):
        """Placeholder functions reject non-operands as arguments."""
        assert_raises(BadCallError, PlaceholderFunction, "func", (),
                      Number(3), Number(6), 1)
        assert_raises(BadCallError, PlaceholderFunction, "func", (), 2,
                      Number(6), Number(3))
        assert_raises(BadCallError, PlaceholderFunction, "func", (),
                      Number(6), 3, Number(3))
    
    def test_equivalence(self):
        """
        Two placeholder functions are equivalent if they have the same name
        and share the namespace.
        
        """
        func1 = PlaceholderFunction("foo", None, String("hi"), Number(4))
        func2 = PlaceholderFunction("foo", None)
        func3 = PlaceholderFunction("Foo", None, String("hi"), Number(4))
        func4 = PlaceholderFunction("Foo", None, Number(4), String("hi"))
        func5 = PlaceholderFunction("baz", None, String("hi"), Number(4))
        func6 = PlaceholderFunction("foo", ["a", "b"], String("hi"), Number(4))
        func7 = PlaceholderFunction("foo", ["a", "b"], String("hi"), Number(4))
        func8 = PlaceholderFunction("foo", ["a", "b"])
        
        ok_(func1 == func1)
        assert_false(func1 == func2)
        ok_(func1 == func3)
        assert_false(func1 == func4)
        assert_false(func1 == func5)
        assert_false(func1 == func6)
        assert_false(func1 == func7)
        assert_false(func1 == func8)
        assert_false(func2 == func1)
        ok_(func2 == func2)
        assert_false(func2 == func3)
        assert_false(func2 == func4)
        assert_false(func2 == func5)
        assert_false(func2 == func6)
        assert_false(func2 == func7)
        assert_false(func2 == func8)
        ok_(func3 == func1)
        assert_false(func3 == func2)
        ok_(func3 == func3)
        assert_false(func3 == func4)
        assert_false(func3 == func5)
        assert_false(func3 == func6)
        assert_false(func3 == func7)
        assert_false(func3 == func8)
        assert_false(func4 == func1)
        assert_false(func4 == func2)
        assert_false(func4 == func3)
        ok_(func4 == func4)
        assert_false(func4 == func5)
        assert_false(func4 == func6)
        assert_false(func4 == func7)
        assert_false(func4 == func8)
        assert_false(func5 == func1)
        assert_false(func5 == func2)
        assert_false(func5 == func3)
        assert_false(func5 == func4)
        ok_(func5 == func5)
        assert_false(func5 == func6)
        assert_false(func5 == func7)
        assert_false(func5 == func8)
        assert_false(func6 == func1)
        assert_false(func6 == func2)
        assert_false(func6 == func3)
        assert_false(func6 == func4)
        assert_false(func6 == func5)
        ok_(func6 == func6)
        ok_(func6 == func7)
        assert_false(func6 == func8)
        assert_false(func7 == func1)
        assert_false(func7 == func2)
        assert_false(func7 == func3)
        assert_false(func7 == func4)
        assert_false(func7 == func5)
        ok_(func7 == func6)
        ok_(func7 == func7)
        assert_false(func7 == func8)
        assert_false(func8 == func1)
        assert_false(func8 == func2)
        assert_false(func8 == func3)
        assert_false(func8 == func4)
        assert_false(func8 == func5)
        assert_false(func8 == func6)
        assert_false(func8 == func7)
        ok_(func8 == func8)
    
    def test_representation_without_namespace(self):
        # With Unicode:
        func = PlaceholderFunction(u"aquí", None, Number(1), String("hi"))
        eq_('<Placeholder function call "aquí"(<Number 1.0>, <String "hi">)>',
            repr(func))
        # With ASCII:
        func = PlaceholderFunction("here", None, Number(1), String("hi"))
        eq_(u'<Placeholder function call "here"(<Number 1.0>, <String "hi">)>',
            repr(func))
    
    def test_representation_with_namespace(self):
        # With Unicode:
        func = PlaceholderFunction(u"aquí", ["a", "d"], Number(1), String("hi"))
        eq_('<Placeholder function call "aquí"(<Number 1.0>, <String "hi">) ' \
            'at namespace="a:d">',
            repr(func))
        # With ASCII:
        func = PlaceholderFunction("here", ["a", "d"], Number(1), String("hi"))
        eq_(u'<Placeholder function call "here"(<Number 1.0>, <String "hi">) ' \
            'at namespace="a:d">',
            repr(func))

