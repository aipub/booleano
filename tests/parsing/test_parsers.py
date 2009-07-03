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
    String, Number, Set, Variable, Function, VariablePlaceholder,
    FunctionPlaceholder)


class TestDefaultGrammar(BaseGrammarTest):
    """
    Tests for the parser of the default/generic grammar.
    
    """
    
    grammar = Grammar()
    
    expressions = {
        # Literals-only expressions:
        '  "a string" == 245    ': Equal(String("a string"), Number(245)),
        '   2 > 5   ': GreaterThan(Number(2), Number(5)),
        # TODO: Identifiers-only expressions:
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
        '{var1, var2}': Set(VariablePlaceholder("var1"),
                            VariablePlaceholder("var2")),
        '{var, "string"}': Set(VariablePlaceholder("var"), String("string")),
        '{3, var, "string"}': Set(Number(3), String("string"),
                                  VariablePlaceholder("var")),
        '{varA, funcB()}': Set(VariablePlaceholder("varA"),
                               FunctionPlaceholder("funcB")),
        '{"hi", 3.1416, len({1, 2, 3, 5, 7}), var0}': Set(
            String("hi"),
            Number(3.1416),
            FunctionPlaceholder("len", (), Set(
                Number(1), Number(2), Number(3), Number(5), Number(7))),
            VariablePlaceholder("var0")
            ),
        # ----- Variables:
        'today': VariablePlaceholder("today"),
        'camelCase': VariablePlaceholder("camelCase"),
        'with_underscore': VariablePlaceholder("with_underscore"),
        ' v1 ': VariablePlaceholder("v1"),
        'var1_here': VariablePlaceholder("var1_here"),
        u'résumé': VariablePlaceholder(u"résumé"),
        u'有容乃大': VariablePlaceholder(u"有容乃大"),
        '    spaces': VariablePlaceholder("spaces"),
        'spaces    ': VariablePlaceholder("spaces"),
        '  spaces  ': VariablePlaceholder("spaces"),
        '_protected_var': VariablePlaceholder("_protected_var"),
        '__private_var': VariablePlaceholder("__private_var"),
        'one_underscore': VariablePlaceholder("one_underscore"),
        'two__underscores__here': VariablePlaceholder("two__underscores__here"),
        'case_insensitive_var': VariablePlaceholder("CASE_INSENSITIVE_VAR"),
        'CASE_INSENSITIVE_VAR': VariablePlaceholder("case_insensitive_var"),
        'cAsE_iNsEnSiTiVe_VaR': VariablePlaceholder("CaSe_InSeNsItIvE_vAr"),
        u'MAYÚSCULA_minúscula': VariablePlaceholder(u"mayúscula_MINÚSCULA"),
        'ns:variable': VariablePlaceholder("variable", ("ns", )),
        'ns0:ns1:variable': VariablePlaceholder("variable", ("ns0", "ns1")),
        'ns0:ns1:ns2:variable': VariablePlaceholder("variable",
                                                    ("ns0", "ns1", "ns2")),
        'ns:sub_ns:variable': VariablePlaceholder("variable", ("ns", "sub_ns")),
        u'ñŝ0:ñŝ1:variable': VariablePlaceholder("variable", (u"ñŝ0", u"ñŝ1")),
        # ----- Functions:
        'stop()': FunctionPlaceholder("stop"),
        'camelCase()': FunctionPlaceholder("camelCase"),
        'with_underscore()': FunctionPlaceholder("with_underscore"),
        ' v1() ': FunctionPlaceholder("v1"),
        'var1_here()': FunctionPlaceholder("var1_here"),
        u'résumé()': FunctionPlaceholder(u"résumé"),
        u'有容乃大()': FunctionPlaceholder(u"有容乃大"),
        '    spaces()': FunctionPlaceholder("spaces"),
        'spaces()    ': FunctionPlaceholder("spaces"),
        '  spaces()  ': FunctionPlaceholder("spaces"),
        '_protected_function()': FunctionPlaceholder("_protected_function"),
        '__private_function()': FunctionPlaceholder("__private_function"),
        'one_underscore()': FunctionPlaceholder("one_underscore"),
        'two__underscores__()': FunctionPlaceholder("two__underscores__"),
        'case_insensitive_func()': FunctionPlaceholder("CASE_INSENSITIVE_FUNC"),
        'CASE_INSENSITIVE_FUNC()': FunctionPlaceholder("case_insensitive_func"),
        'cAsE_iNsEnSiTiVe_FuNc()': FunctionPlaceholder("CaSe_InSeNsItIvE_fUnC"),
        u'MAYÚSCULA_minúscula()': FunctionPlaceholder(u"mayúscula_MINÚSCULA"),
        'func("argument")': FunctionPlaceholder("func", (), String("argument")),
        u'función("arg1", variable, 3)': FunctionPlaceholder(u"función",
            (),
            String("arg1"),
            VariablePlaceholder("variable"),
            Number(3),
            ),
        u'función("arg1", sub_función(), 3.0)': FunctionPlaceholder(u"función",
            (),
            String("arg1"),
            FunctionPlaceholder(u"sub_función"),
            Number(3),
            ),
        'ns:function()': FunctionPlaceholder("function", ("ns", )),
        'ns0:ns1:function()': FunctionPlaceholder("function", ("ns0", "ns1")),
        'ns0:ns1:ns2:function()': FunctionPlaceholder("function",
                                                      ("ns0", "ns1", "ns2")),
        'ns:sub_ns:function("with argument")': FunctionPlaceholder("function",
            ("ns", "sub_ns"),
            String("with argument"),
            ),
        u'ñŝ:ñś1:function()': FunctionPlaceholder("function", (u"ñŝ", u"ñś1")),
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

