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
Test suite for the built-in parser implementation.

"""

from booleano.parser import Grammar
from booleano.parser.scope import Namespace
from booleano.parser.testutils import BaseGrammarTest
from booleano.operations import (Truth, Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset,
    String, Number, Set, Variable, Function, PlaceholderVariable,
    PlaceholderFunction)


class TestDefaultGrammar(BaseGrammarTest):
    """
    Tests for the parser of the default/generic grammar.
    
    """
    
    grammar = Grammar()
    
    expressions = {
        # Literals-only expressions:
        '  "a string" == 245    ': Equal(String("a string"), Number(245)),
        '   2 > 5   ': GreaterThan(Number(2), Number(5)),
        # Identifiers-only expressions:
        '  today > yesterday ': GreaterThan(PlaceholderVariable("today"),
                                            PlaceholderVariable("yesterday")),
        'time:today > time:yesterday ': GreaterThan(
            PlaceholderVariable("today", ("time", )),
            PlaceholderVariable("yesterday", ("time", ))),
        # Literals + non-literal expressions:
        'today > "1999-06-01"': GreaterThan(PlaceholderVariable("today"),
                                            String("1999-06-01")),
        'get_parents("Gustavo") == {"Liliana", "Carlos"}': Equal(
            PlaceholderFunction("get_parents", None, String("Gustavo")),
            Set(String("Liliana"), String("Carlos"))
            ),
        # Relational operations:
        'now == today:time': Equal(PlaceholderVariable("now"),
                                   PlaceholderVariable("time", ("today", ))),
        '3.1416 == Pi': Equal(Number(3.1416), PlaceholderVariable("pi")),
        'Pi == 3.1416': Equal(PlaceholderVariable("pi"), Number(3.1416)),
        'days:today != days:yesterday': NotEqual(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 != Pi': NotEqual(Number(3.0), PlaceholderVariable("pi")),
        'Pi != 3.00': Equal(PlaceholderVariable("pi"), Number(3.00)),
        'days:today > days:yesterday': GreaterThan(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 > Pi': GreaterThan(Number(3.0), PlaceholderVariable("pi")),
        'Pi > 3.00': GreaterThan(PlaceholderVariable("pi"), Number(3.00)),
        'days:today < days:yesterday': LessThan(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 < Pi': LessThan(Number(3.0), PlaceholderVariable("pi")),
        'Pi < 3.00': LessThan(PlaceholderVariable("pi"), Number(3.00)),
        'days:today >= days:yesterday': GreaterEqual(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 >= Pi': GreaterEqual(Number(3.0), PlaceholderVariable("pi")),
        'Pi >= 3.00': GreaterEqual(PlaceholderVariable("pi"), Number(3.00)),
        'days:today <= days:yesterday': LessEqual(
            PlaceholderVariable("today", ("days",)),
            PlaceholderVariable("yesterday", ("days",))),
        '3.00 <= Pi': LessEqual(Number(3.0), PlaceholderVariable("pi")),
        'Pi <= 3.00': LessEqual(PlaceholderVariable("pi"), Number(3.00)),
    }
    
    single_operands = {
        # ----- Strings
        '"oneword"': String("oneword"),
        '"double quotes"': String("double quotes"),
        "'single quotes'": String("single quotes"),
        "''": String(""),
        '""': String(""),
        "'something with \"quotes\"'": String('something with "quotes"'),
        '"something with \'quotes\'"': String("something with 'quotes'"),
        u'"áéíóúñçÁÉÍÓÚÑÇ"': String(u"áéíóúñçÁÉÍÓÚÑÇ"),
        u'"海納百川，有容乃大"': String(u"海納百川，有容乃大"),
        u"'مقالة مختارة'": String(u"مقالة مختارة"),
        u'"вільної енциклопедії"': String(u"вільної енциклопедії"),
        # ----- Numbers
        '1': Number(1),
        '01': Number(1),
        '5000': Number(5000),
        '+3': Number(3),
        '-3': Number(-3),
        '2.34': Number(2.34),
        '2.2': Number(2.2),
        '+3.1416': Number(3.1416),
        '-3.1416': Number(-3.1416),
        '5,000': Number(5000),
        '1,000,000.34': Number(1000000.34),
        '+1,000,000.22': Number(1000000.22),
        '-1,000,000.22': Number(-1000000.22),
        # ----- Sets:
        ' {} ': Set(),
        '{{}, {}}': Set(Set(), Set()),
        '{1,000, 3.05}': Set(Number(1000), Number(3.05)),
        '{1,234,567}': Set(Number(1234567)),
        '{23,24,25}': Set(Number(23), Number(24), Number(25)),
        '{100, 200, 300}': Set(Number(100), Number(200), Number(300)),
        '{1, 2, {"orange", "apple"}, 3}': Set(
            Number(1),
            Number(2),
            Number(3),
            Set(String("orange"), String("apple"))
            ),
        u'{"españa", {"caracas", {"las chimeneas", "el trigal"}}, "france"}': \
            Set(
                String(u"españa"),
                String("france"),
                Set(
                    String("caracas"),
                    Set(String("el trigal"), String("las chimeneas"))
                ),
            ),
        '{var1, var2}': Set(PlaceholderVariable("var1"),
                            PlaceholderVariable("var2")),
        '{var, "string"}': Set(PlaceholderVariable("var"), String("string")),
        '{3, var, "string"}': Set(Number(3), String("string"),
                                  PlaceholderVariable("var")),
        '{varA, funcB()}': Set(PlaceholderVariable("varA"),
                               PlaceholderFunction("funcB")),
        '{"hi", 3.1416, len({1, 2, 3, 5, 7}), var0}': Set(
            String("hi"),
            Number(3.1416),
            PlaceholderFunction("len", (), Set(
                Number(1), Number(2), Number(3), Number(5), Number(7))),
            PlaceholderVariable("var0")
            ),
        # ----- Variables:
        'today': PlaceholderVariable("today"),
        'camelCase': PlaceholderVariable("camelCase"),
        'with_underscore': PlaceholderVariable("with_underscore"),
        ' v1 ': PlaceholderVariable("v1"),
        'var1_here': PlaceholderVariable("var1_here"),
        u'résumé': PlaceholderVariable(u"résumé"),
        u'有容乃大': PlaceholderVariable(u"有容乃大"),
        '    spaces': PlaceholderVariable("spaces"),
        'spaces    ': PlaceholderVariable("spaces"),
        '  spaces  ': PlaceholderVariable("spaces"),
        '_protected_var': PlaceholderVariable("_protected_var"),
        '__private_var': PlaceholderVariable("__private_var"),
        'one_underscore': PlaceholderVariable("one_underscore"),
        'two__underscores__here': PlaceholderVariable("two__underscores__here"),
        'case_insensitive_var': PlaceholderVariable("CASE_INSENSITIVE_VAR"),
        'CASE_INSENSITIVE_VAR': PlaceholderVariable("case_insensitive_var"),
        'cAsE_iNsEnSiTiVe_VaR': PlaceholderVariable("CaSe_InSeNsItIvE_vAr"),
        u'MAYÚSCULA_minúscula': PlaceholderVariable(u"mayúscula_MINÚSCULA"),
        'ns:variable': PlaceholderVariable("variable", ("ns", )),
        'ns0:ns1:variable': PlaceholderVariable("variable", ("ns0", "ns1")),
        'ns0:ns1:ns2:variable': PlaceholderVariable("variable",
                                                    ("ns0", "ns1", "ns2")),
        'ns:sub_ns:variable': PlaceholderVariable("variable", ("ns", "sub_ns")),
        u'ñŝ0:ñŝ1:variable': PlaceholderVariable("variable", (u"ñŝ0", u"ñŝ1")),
        # ----- Functions:
        'stop()': PlaceholderFunction("stop"),
        'stop ()': PlaceholderFunction("stop"),
        'stop( )': PlaceholderFunction("stop"),
        'stop ( )': PlaceholderFunction("stop"),
        'camelCase()': PlaceholderFunction("camelCase"),
        'with_underscore()': PlaceholderFunction("with_underscore"),
        ' v1() ': PlaceholderFunction("v1"),
        'var1_here()': PlaceholderFunction("var1_here"),
        u'résumé()': PlaceholderFunction(u"résumé"),
        u'有容乃大()': PlaceholderFunction(u"有容乃大"),
        '    spaces()': PlaceholderFunction("spaces"),
        'spaces()    ': PlaceholderFunction("spaces"),
        '  spaces()  ': PlaceholderFunction("spaces"),
        '_protected_function()': PlaceholderFunction("_protected_function"),
        '__private_function()': PlaceholderFunction("__private_function"),
        'one_underscore()': PlaceholderFunction("one_underscore"),
        'two__underscores__()': PlaceholderFunction("two__underscores__"),
        'case_insensitive_func()': PlaceholderFunction("CASE_INSENSITIVE_FUNC"),
        'CASE_INSENSITIVE_FUNC()': PlaceholderFunction("case_insensitive_func"),
        'cAsE_iNsEnSiTiVe_FuNc()': PlaceholderFunction("CaSe_InSeNsItIvE_fUnC"),
        u'MAYÚSCULA_minúscula()': PlaceholderFunction(u"mayúscula_MINÚSCULA"),
        'func("argument")': PlaceholderFunction("func", (), String("argument")),
        'function("arg1", variable, 3)': PlaceholderFunction("function",
            (),
            String("arg1"),
            PlaceholderVariable("variable"),
            Number(3),
            ),
        'function("arg1", ns:variable, 3)': PlaceholderFunction(
            "function",
            (),
            String("arg1"),
            PlaceholderVariable("variable", ("ns", )),
            Number(3),
            ),
        'ns:function("arg1", ns:variable, 3)': PlaceholderFunction(
            "function",
            ("ns", ),
            String("arg1"),
            PlaceholderVariable("variable", ("ns", )),
            Number(3),
            ),
        'function("arg1", ns:sub_function(), 3.0)': PlaceholderFunction(
            "function",
            (),
            String("arg1"),
            PlaceholderFunction("sub_function", ("ns", )),
            Number(3),
            ),
        'ns:function("arg1", ns:sub_function(), 3.0)': PlaceholderFunction(
            "function",
            ("ns", ),
            String("arg1"),
            PlaceholderFunction("sub_function", ("ns", )),
            Number(3),
            ),
        'ns:function()': PlaceholderFunction("function", ("ns", )),
        'ns0:ns1:function()': PlaceholderFunction("function", ("ns0", "ns1")),
        'ns0:ns1:ns2:function()': PlaceholderFunction("function",
                                                      ("ns0", "ns1", "ns2")),
        'ns:sub_ns:function("with argument")': PlaceholderFunction("function",
            ("ns", "sub_ns"),
            String("with argument"),
            ),
        u'ñŝ:ñś1:function()': PlaceholderFunction("function", (u"ñŝ", u"ñś1")),
        u'ñŝ:ñś1:función()': PlaceholderFunction(u"función", (u"ñŝ", u"ñś1")),
    }
    
    invalid_operands = (
        # Invalid strings:
        '\'mixed quotes"',
        # Invalid numbers:
        "3 . 1416",
        "3. 1416",
        "3 .1416",
        "1,00",
        "12.4,500,000",
        # Invalid variables:
        "dashes-here-cant-you-see-them",
        "1st_variable",
        "25th_variable",
        "namespace-here:variable",
        "1stnamespace:var",
        "global:2ndlevel:var",
        "namespace:1st_variable",
        # Invalid functions:
        "func(",
        "func)",
        "func)(",
        "func[]",
        "func{}",
        "func(,)",
        "func(arg1, )",
        "func(, arg2)",
        "func(, arg2, )",
        "function-name()",
        "1st_function()",
        "25th_function()",
        "namespace-here:function()",
        "1stnamespace:function()",
        "global:2ndlevel:function()",
        "namespace:1st_function()",
        "foo( bad-namespace:baz() )",
        # Invalid sets:
        "[]",
        "{]",
        "[}",
        "}{",
        "{key: 'value'}",
        "[element1, element2, element3]",
        "{element 1, element 2}",
        "{element1; element2; element3}",
        "{element == 'string'}",
        # Miscellaneous:
        "-",
        "this is definitely not an operand",
    )

