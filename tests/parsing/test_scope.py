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
Scope handling tests.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises, raises

from booleano.parser.scope import Bind, Namespace, SymbolTable
from booleano.operations import String, Number
from booleano.exc import ScopeError

from tests import (TrafficLightVar, PermissiveFunction, TrafficViolationFunc,
                   BoolVar)


class TestBind(object):
    """Tests for operand binder."""
    
    def test_global_names(self):
        """When an operand is bound, its global name must be set accordingly."""
        operand = String("hey there")
        bind1 = Bind("da_global_name", operand)
        bind2 = Bind("Da_Global_Name", operand)
        eq_(bind1.global_name, "da_global_name")
        eq_(bind1.global_name, bind2.global_name)
    
    def test_names(self):
        """
        When an operand is bound, its multiple names must be set accordingly.
        
        """
        operand = String("Vive la france !")
        # No localized names:
        bind1 = Bind("foo", operand)
        eq_(bind1.names, {})
        # Lower-case names:
        names0 = {'es_VE': "cartuchera", 'es_ES': "estuche"}
        bind2 = Bind("bar", operand, **names0)
        eq_(bind2.names, names0)
        # Mixed-case names -- must be converted to lower-case:
        names1 = {'es_VE': "Cartuchera", 'es_ES': "estuche"}
        bind2 = Bind("bar", operand, **names1)
        eq_(bind2.names, names0)
    
    def test_no_default_namespace(self):
        """Operand bindings must not be in a namespace by default."""
        bind = Bind("foo", String("whatever"))
        eq_(bind.namespace, None)
    
    def test_constant(self):
        """Constants can be bound."""
        constant = String("I'm a string!")
        bound_constant = Bind("da_string", constant)
        eq_(bound_constant.operand, constant)
    
    def test_instance(self):
        """Class instances can be bound."""
        instance = TrafficLightVar()
        bound_instance = Bind("da_variable", instance)
        eq_(bound_instance.operand, instance)
    
    def test_equality(self):
        """Two bindings are equivalent if they have the same names."""
        op1 = TrafficLightVar()
        op2 = String("hey, where's my car?")
        bind1 = Bind("name1", op1)
        bind2 = Bind("name2", op2)
        bind3 = Bind("name2", op1)
        bind4 = Bind("name1", op2)
        bind5 = Bind("name1", op1)
        bind6 = Bind("name2", op2)
        bind7 = Bind("name1", op1, es="nombre1")
        bind8 = Bind("name1", op1, es_VE="nombre1", es="nombre1")
        bind9 = Bind("name1", op1, es="nombre1")
        
        ok_(bind1 == bind4)
        ok_(bind1 == bind5)
        ok_(bind2 == bind3)
        ok_(bind2 == bind6)
        ok_(bind3 == bind2)
        ok_(bind3 == bind6)
        ok_(bind4 == bind1)
        ok_(bind4 == bind5)
        ok_(bind5 == bind5)
        ok_(bind5 == bind1)
        ok_(bind5 == bind4)
        ok_(bind6 == bind2)
        ok_(bind6 == bind3)
        ok_(bind7 == bind9)
        ok_(bind9 == bind7)
        
        ok_(bind1 != None)
        ok_(bind1 != Namespace("name1", []))
        
        ok_(bind1 != bind2)
        ok_(bind1 != bind3)
        ok_(bind1 != bind6)
        ok_(bind1 != bind7)
        ok_(bind1 != bind8)
        ok_(bind1 != bind9)
        ok_(bind2 != bind1)
        ok_(bind2 != bind4)
        ok_(bind2 != bind5)
        ok_(bind2 != bind7)
        ok_(bind2 != bind8)
        ok_(bind2 != bind9)
        ok_(bind3 != bind1)
        ok_(bind3 != bind4)
        ok_(bind3 != bind5)
        ok_(bind3 != bind7)
        ok_(bind3 != bind8)
        ok_(bind3 != bind9)
        ok_(bind4 != bind2)
        ok_(bind4 != bind3)
        ok_(bind4 != bind6)
        ok_(bind4 != bind7)
        ok_(bind4 != bind8)
        ok_(bind4 != bind9)
        ok_(bind5 != bind2)
        ok_(bind5 != bind3)
        ok_(bind5 != bind6)
        ok_(bind5 != bind7)
        ok_(bind5 != bind8)
        ok_(bind5 != bind9)
        ok_(bind6 != bind1)
        ok_(bind6 != bind4)
        ok_(bind6 != bind5)
        ok_(bind6 != bind7)
        ok_(bind6 != bind8)
        ok_(bind6 != bind9)
        ok_(bind7 != bind1)
        ok_(bind7 != bind2)
        ok_(bind7 != bind3)
        ok_(bind7 != bind4)
        ok_(bind7 != bind5)
        ok_(bind7 != bind6)
        ok_(bind7 != bind8)
        ok_(bind8 != bind1)
        ok_(bind8 != bind2)
        ok_(bind8 != bind3)
        ok_(bind8 != bind4)
        ok_(bind8 != bind5)
        ok_(bind8 != bind6)
        ok_(bind8 != bind7)
        ok_(bind8 != bind9)
        ok_(bind9 != bind1)
        ok_(bind9 != bind2)
        ok_(bind9 != bind3)
        ok_(bind9 != bind4)
        ok_(bind9 != bind5)
        ok_(bind9 != bind6)
        ok_(bind9 != bind8)
    
    def test_string_without_namespace(self):
        # With ASCII characters:
        bind1 = Bind("pi", Number(3.1416))
        bind1_as_unicode = unicode(bind1)
        eq_(bind1_as_unicode, 'Operand 3.1416 bound as "pi"')
        eq_(bind1_as_unicode, str(bind1))
        # With non-ASCII characters:
        bind2 = Bind(u"pí", Number(3.1416))
        bind2_as_unicode = unicode(bind2)
        eq_(bind2_as_unicode, u'Operand 3.1416 bound as "pí"')
        eq_(str(bind2), 'Operand 3.1416 bound as "pí"')
    
    def test_string_with_namespace(self):
        # With ASCII characters:
        bind1 = Bind("pi", Number(3.1416))
        Namespace("global", [bind1])
        bind1_as_unicode = unicode(bind1)
        eq_('Operand 3.1416 bound as "pi" (at Namespace global)',
            bind1_as_unicode)
        eq_(str(bind1), bind1_as_unicode)
        # With non-ASCII characters:
        bind2 = Bind(u"pí", Number(3.1416))
        Namespace("global", [bind2])
        bind2_as_unicode = unicode(bind2)
        eq_(u'Operand 3.1416 bound as "pí" (at Namespace global)',
            bind2_as_unicode)
        eq_('Operand 3.1416 bound as "pí" (at Namespace global)', str(bind2))


class TestNamespace(object):
    """Tests for the multilingual namespaces."""
    
    def test_global_names(self):
        """
        When a namespace is created, its global name must be set accordingly.
        
        """
        ns1 = Namespace("foo", [])
        ns2 = Namespace("Foo", [])
        eq_(ns1.global_name, "foo")
        eq_(ns1.global_name, ns2.global_name)
    
    def test_names(self):
        """
        When a namespace is created, its multiple names must be set accordingly.
        
        """
        # No localized names:
        ns0 = Namespace("foo", [])
        eq_(ns0.names, {})
        # Lower-case names:
        names0 = {'es_VE': "cartuchera", 'es_ES': "estuche"}
        ns1 = Namespace("bar", [], **names0)
        eq_(ns1.names, names0)
        # Mixed-case names -- must be converted to lower-case:
        names1 = {'es_VE': "Cartuchera", 'es_ES': "estuche"}
        ns2 = Namespace("bar", [], **names1)
        eq_(ns2.names, names0)
    
    def test_no_default_namespace(self):
        """Namespaces must not have a parent namespace by default."""
        ns = Namespace("foo", [])
        eq_(ns.namespace, None)
    
    def test_constructor_without_subnamespaces(self):
        """Sub-namespaces are optional."""
        ns = Namespace("foo", [])
        eq_(len(ns.subnamespaces), 0)
    
    def test_constructor_without_objects(self):
        """Objects are mandatory, or an empty list must be passed explicitly."""
        # No objects
        assert_raises(TypeError, Namespace, "foo")
        # Empty list of objects:
        ns = Namespace("foo", [])
        eq_(len(ns.objects), 0)
    
    def test_constructor_with_objects(self):
        objects = [Bind("greeting", String("hey")),
                   Bind("traffic", TrafficLightVar())]
        ns = Namespace("global", objects)
        eq_(ns.objects, set(objects))
    
    def test_constructor_with_namespaces(self):
        namespaces = set([
            Namespace("sub1", []),
            Namespace(
                "sub2",
                [],
                [Namespace("sub2.sub1", []), Namespace("sub2.sub2", [])]
            ),
        ])
        ns = Namespace("global", [], namespaces)
        eq_(ns.subnamespaces, namespaces)
    
    def test_duplicate_objects(self):
        """There must be no duplicate object."""
        # In the constructor:
        objects1 = [Bind("salutation", String("hey")),
                    Bind("traffic", TrafficLightVar()),
                    Bind("salutation", String("hey"))]
        assert_raises(ScopeError, Namespace, "global", objects1)
        # Post-instantiation:
        objects2 = [Bind("salutation", String("hey")),
                    Bind("traffic", TrafficLightVar())]
        ns = Namespace("global", objects2)
        assert_raises(ScopeError, ns.add_object,
                      Bind("salutation", String("hey")))
    
    def test_duplicate_subnamespaces(self):
        """There must not be duplicate subnamespaces."""
        # In the constructor:
        subnamespaces1 = [Namespace("foo", ()),
                          Namespace("bar", ()),
                          Namespace("foo", ())]
        assert_raises(ScopeError, Namespace, "global", (), subnamespaces1)
        # Post-instantiation:
        subnamespaces2 = [Namespace("foo", ()),
                          Namespace("bar", ())]
        ns = Namespace("global", [], subnamespaces2)
        assert_raises(ScopeError, ns.add_namespace, Namespace("bar", []))
    
    def test_unreusable_bindings(self):
        """
        Operand bindings and namespaces can only be bound to a single parent
        namespace.
        
        """
        # An operand binding:
        bind = Bind("traffic-light", TrafficLightVar())
        Namespace("traffic", [bind])
        assert_raises(ScopeError, Namespace, "baz", [bind])
        # A namespace:
        ns0 = Namespace("foo", [])
        Namespace("global", [], [ns0])
        assert_raises(ScopeError, Namespace, "bar", [], [ns0])
    
    def test_checking_valid_namespace(self):
        ns = Namespace("global",
            # Bindings/global objects:
            (
             Bind("bool", BoolVar(), es="booleano"),
             Bind("traffic", TrafficLightVar(), es=u"tráfico"),
            ),
            # Sub-namespaces:
            (
             Namespace("maths",
                (
                 Bind("pi", Number(3.1416)),
                 Bind("e", Number(2.7183)),
                ),
             ),
            )
        )
        eq_(ns.validate_scope(), None)
    
    def test_checking_object_and_subnamespace_sharing_global_name(self):
        """
        It's valid for an object and a subnamespace to share the global name.
        
        """
        ns = Namespace("global",
            (
                Bind("today", BoolVar()),
            ),
            (
                Namespace("today", ()),
            )
        )
        eq_(ns.validate_scope(), None)
    
    def test_checking_object_and_subnamespace_sharing_localized_name(self):
        """
        It's valid for an object and a subnamespace to share the localized name.
        
        """
        ns1 = Namespace("global",
            (
                Bind("current_day", BoolVar(), es="hoy"),
            ),
            (
                Namespace("today", (), es="hoy"),
            )
        )
        ns2 = Namespace("global",
            (
                Bind("current_day", BoolVar(), es="hoy"),
            ),
            (
                # This namespace will be called "hoy" in Spanish too:
                Namespace("hoy", ()),
            )
        )
        eq_(ns1.validate_scope(), None)
        eq_(ns2.validate_scope(), None)
    
    def test_namespace_with_duplicate_object_global_names(self):
        """
        Two objects cannot have the same global names in the same namespace.
        
        """
        ns = Namespace("global",
            (
                Bind("e", Number(2.7183), es_VE=u"número e"),
                Bind("pi", Number(3.1416)),
                Bind("e", Number(2.71828), es_ES=u"número e"),
            ),
        )
        assert_raises(ScopeError, ns.validate_scope)
    
    def test_namespace_with_duplicate_object_global_names(self):
        """
        Two objects cannot have the same global names in the same namespace.
        
        """
        ns = Namespace("global",
            (
                Bind("e", Number(2.7183), es_VE=u"número e"),
                Bind("pi", Number(3.1416)),
                Bind("e", Number(2.71828), es_ES=u"número e"),
            ),
        )
        assert_raises(ScopeError, ns.validate_scope)
    
    def test_namespace_with_duplicate_object_localized_names(self):
        """
        Two objects cannot have the same localized names in the same namespace.
        
        """
        ns1 = Namespace("global",
            (
                Bind("e", Number(2.7183), es_VE=u"número e"),
                Bind("pi", Number(3.1416)),
                Bind("eulers-number", Number(2.71828), es_VE=u"número e"),
            ),
        )
        ns2 = Namespace("global",
            (
                Bind("e", Number(2.7183), es_VE=u"número e"),
                Bind("pi", Number(3.1416)),
                # These object will be called "número e" in Spanish too:
                Bind(u"número e", Number(2.71828)),
            ),
        )
        assert_raises(ScopeError, ns1.validate_scope)
        assert_raises(ScopeError, ns2.validate_scope)
    
    def test_namespace_with_duplicate_namespace_global_names(self):
        """
        Two subnamespaces cannot have the same global names in the same
        parent namespace.
        
        """
        ns = Namespace("global",
            (),
            (
                Namespace("maths", ()),
                Namespace("computing", ()),
                Namespace("maths", (), es=u"matemática"),
            )
        )
        assert_raises(ScopeError, ns.validate_scope)
    
    def test_namespace_with_duplicate_namespace_localized_names(self):
        """
        Two subnamespaces cannot have the same global names in the same
        parent namespace.
        
        """
        ns1 = Namespace("global",
            (),
            (
                Namespace("maths", (), es=u"matemática"),
                Namespace("computing", ()),
                Namespace("mathematics", (), es=u"matemática"),
            )
        )
        ns2 = Namespace("global",
            (),
            (
                Namespace("maths", (), es=u"matemática"),
                Namespace("computing", ()),
                # This namespace will be called "matemática" in Spanish too:
                Namespace(u"matemática", ()),
            )
        )
        assert_raises(ScopeError, ns1.validate_scope)
        assert_raises(ScopeError, ns2.validate_scope)
    
    def test_name_clash_in_grand_children(self):
        """
        The scope must be validated even inside the subnamespaces.
        
        """
        sciences_ns1 = Namespace("sciences",
            (),
            (
                Namespace("maths", (), es=u"matemática"),
                Namespace("computing", ()),
                Namespace("maths", ()),
            )
        )
        sciences_ns2 = Namespace("sciences",
            (),
            (
                Namespace("maths", (), es=u"matemática"),
                Namespace("computing", ()),
                Namespace("mathematics", (), es=u"matemática"),
            )
        )
        sciences_ns3 = Namespace("sciences",
            (),
            (
                Namespace("maths", (), es=u"matemática"),
                Namespace("computing", ()),
                # This namespace will be called "matemática" in Spanish too:
                Namespace(u"matemática", ()),
            )
        )
        # Now a name clash at the objects level:
        sciences_ns4 = Namespace("global",
            (
                Bind("foo", BoolVar()),
                Bind("foo", TrafficLightVar(), es="bar"),
            )
        )
        
        ns1 = Namespace("global", (), (sciences_ns1, Namespace("society", ())))
        ns2 = Namespace("global", (), (sciences_ns2, Namespace("society", ())))
        ns3 = Namespace("global", (), (sciences_ns3, Namespace("society", ())))
        ns4 = Namespace("global", (), (sciences_ns4, ))
        
        assert_raises(ScopeError, ns1.validate_scope)
        assert_raises(ScopeError, ns2.validate_scope)
        assert_raises(ScopeError, ns3.validate_scope)
        assert_raises(ScopeError, ns4.validate_scope)
    
    def test_equivalence(self):
        objects1 = lambda: [Bind("dish", String("cachapa")),
                            Bind("drink", String("empanada"))]
        objects2 = lambda: [Bind("drink", String("empanada")),
                            Bind("dish", String("cachapa"))]
        objects3 = lambda: [Bind("pi", Number(3.1416))]
        
        ns1 = Namespace("foo", objects1())
        ns2 = Namespace("foo", objects1(), ())
        ns3 = Namespace("foo", objects1(), es="fulano")
        ns4 = Namespace("foo", objects1(), [], es="fulano")
        ns5 = Namespace("foo", objects2())
        ns6 = Namespace("foo", objects3())
        ns7 = Namespace("foo", objects2(), es="fulano")
        ns8 = Namespace("foo", objects3(), es_VE="fulano")
        ns9 = Namespace("bar", objects1())
        ns10 = Namespace("foo", objects1())
        ns11 = Namespace(
            "foo", objects1(), [Namespace("bar", []), Namespace("baz", [])])
        ns12 = Namespace(
            "foo", objects1(), [Namespace("baz", []), Namespace("bar", [])])
        
        # Moving ns10 into the "baz" namespace:
        Namespace("baz", [], [ns10])
        
        ok_(ns1 == ns2)
        ok_(ns1 == ns5)
        ok_(ns1 == ns10)
        ok_(ns2 == ns1)
        ok_(ns2 == ns5)
        ok_(ns2 == ns10)
        ok_(ns3 == ns4)
        ok_(ns3 == ns7)
        ok_(ns4 == ns3)
        ok_(ns4 == ns7)
        ok_(ns5 == ns1)
        ok_(ns5 == ns2)
        ok_(ns5 == ns10)
        ok_(ns7 == ns3)
        ok_(ns7 == ns4)
        ok_(ns10 == ns1)
        ok_(ns10 == ns2)
        ok_(ns10 == ns5)
        ok_(ns11 == ns12)
        ok_(ns12 == ns11)
        
        ok_(ns1 != None)
        ok_(ns1 != Bind("foo", String("cachapa")))
        
        ok_(ns1 != ns3)
        ok_(ns1 != ns4)
        ok_(ns1 != ns6)
        ok_(ns1 != ns7)
        ok_(ns1 != ns8)
        ok_(ns1 != ns9)
        ok_(ns1 != ns11)
        ok_(ns1 != ns12)
        ok_(ns2 != ns3)
        ok_(ns2 != ns4)
        ok_(ns2 != ns6)
        ok_(ns2 != ns7)
        ok_(ns2 != ns8)
        ok_(ns2 != ns9)
        ok_(ns2 != ns11)
        ok_(ns2 != ns12)
        ok_(ns3 != ns1)
        ok_(ns3 != ns2)
        ok_(ns3 != ns5)
        ok_(ns3 != ns6)
        ok_(ns3 != ns8)
        ok_(ns3 != ns9)
        ok_(ns3 != ns10)
        ok_(ns3 != ns11)
        ok_(ns3 != ns12)
        ok_(ns4 != ns1)
        ok_(ns4 != ns2)
        ok_(ns4 != ns5)
        ok_(ns4 != ns6)
        ok_(ns4 != ns8)
        ok_(ns4 != ns9)
        ok_(ns4 != ns10)
        ok_(ns4 != ns11)
        ok_(ns4 != ns12)
        ok_(ns5 != ns3)
        ok_(ns5 != ns4)
        ok_(ns5 != ns6)
        ok_(ns5 != ns7)
        ok_(ns5 != ns8)
        ok_(ns5 != ns9)
        ok_(ns5 != ns11)
        ok_(ns5 != ns12)
        ok_(ns6 != ns1)
        ok_(ns6 != ns2)
        ok_(ns6 != ns3)
        ok_(ns6 != ns4)
        ok_(ns6 != ns5)
        ok_(ns6 != ns7)
        ok_(ns6 != ns8)
        ok_(ns6 != ns9)
        ok_(ns6 != ns10)
        ok_(ns6 != ns11)
        ok_(ns6 != ns12)
        ok_(ns7 != ns1)
        ok_(ns7 != ns2)
        ok_(ns7 != ns5)
        ok_(ns7 != ns6)
        ok_(ns7 != ns8)
        ok_(ns7 != ns9)
        ok_(ns7 != ns10)
        ok_(ns7 != ns11)
        ok_(ns7 != ns12)
        ok_(ns8 != ns1)
        ok_(ns8 != ns2)
        ok_(ns8 != ns3)
        ok_(ns8 != ns4)
        ok_(ns8 != ns5)
        ok_(ns8 != ns6)
        ok_(ns8 != ns7)
        ok_(ns8 != ns9)
        ok_(ns8 != ns10)
        ok_(ns8 != ns11)
        ok_(ns8 != ns12)
        ok_(ns9 != ns1)
        ok_(ns9 != ns2)
        ok_(ns9 != ns3)
        ok_(ns9 != ns4)
        ok_(ns9 != ns5)
        ok_(ns9 != ns6)
        ok_(ns9 != ns7)
        ok_(ns9 != ns8)
        ok_(ns9 != ns10)
        ok_(ns9 != ns11)
        ok_(ns9 != ns12)
        ok_(ns10 != ns3)
        ok_(ns10 != ns4)
        ok_(ns10 != ns6)
        ok_(ns10 != ns7)
        ok_(ns10 != ns8)
        ok_(ns10 != ns9)
        ok_(ns11 != ns1)
        ok_(ns11 != ns2)
        ok_(ns11 != ns3)
        ok_(ns11 != ns4)
        ok_(ns11 != ns5)
        ok_(ns11 != ns6)
        ok_(ns11 != ns7)
        ok_(ns11 != ns8)
        ok_(ns11 != ns9)
        ok_(ns11 != ns10)
        ok_(ns12 != ns1)
        ok_(ns12 != ns2)
        ok_(ns12 != ns3)
        ok_(ns12 != ns4)
        ok_(ns12 != ns5)
        ok_(ns12 != ns6)
        ok_(ns12 != ns7)
        ok_(ns12 != ns8)
        ok_(ns12 != ns9)
        ok_(ns12 != ns10)
    
    def test_string(self):
        # With ASCII names:
        ns2 = Namespace("grand-child", [])
        ns1 = Namespace("parent", (), [ns2])
        ns0 = Namespace("global", (), [ns1])
        eq_(str(ns0), "Namespace global")
        eq_(str(ns1), "Namespace global:parent")
        eq_(str(ns2), "Namespace global:parent:grand-child")
        # With Unicode characters:
        ns2 = Namespace(u"gránd-chíld", [])
        ns1 = Namespace(u"párênt", (), [ns2])
        ns0 = Namespace(u"glòbál", (), [ns1])
        eq_(str(ns0), "Namespace glòbál")
        eq_(str(ns1), "Namespace glòbál:párênt")
        eq_(str(ns2), "Namespace glòbál:párênt:gránd-chíld")
    
    def test_unicode(self):
        # With ASCII names:
        ns2 = Namespace("grand-child", [])
        ns1 = Namespace("parent", (), [ns2])
        ns0 = Namespace("global", (), [ns1])
        eq_(unicode(ns0), "Namespace global")
        eq_(unicode(ns1), "Namespace global:parent")
        eq_(unicode(ns2), "Namespace global:parent:grand-child")
        # With Unicode characters:
        ns2 = Namespace(u"gránd-chíld", [])
        ns1 = Namespace(u"párênt", (), [ns2])
        ns0 = Namespace(u"glòbál", (), [ns1])
        eq_(unicode(ns0), u"Namespace glòbál")
        eq_(unicode(ns1), u"Namespace glòbál:párênt")
        eq_(unicode(ns2), u"Namespace glòbál:párênt:gránd-chíld")

