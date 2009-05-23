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
Test suite for the generic grammar.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises

from booleano.parser.syntaxes import GenericGrammar
from booleano.parser.testutils import BaseParseTest
from booleano.operations.operators import (FunctionOperator, TruthOperator,
    NotOperator, AndOperator, OrOperator, XorOperator, EqualOperator,
    LessThanOperator, GreaterThanOperator, LessEqualOperator, 
    GreaterEqualOperator, ContainsOperator, SubsetOperator)
from booleano.operations.operands import (String, Number, Set, Variable)


class TestParsing(BaseParseTest):
    """
    Tests for the parser of the generic grammar.
    
    """
    grammar = GenericGrammar()
    
    expressions = {
        '  "a string"     ': String("a string"),
        '   2   ': Number(2),
        ' last_night': Variable("last_night"),
        }
    
    valid_operands = {
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
        # ----- Variables:
        'today': Variable("today"),
        'camelCase': Variable("camelCase"),
        'with_underscore': Variable("with_underscore"),
        u'résumé': Variable(u"résumé"),
        u'有容乃大': Variable(u"有容乃大"),
        '    spaces': Variable("spaces"),
        'spaces    ': Variable("spaces"),
        '  spaces  ': Variable("spaces"),
        '1st_variable': Variable("1st_variable"),
        '25th_variable': Variable("25th_variable"),
        '_protected_var': Variable("_protected_var"),
        '__private_var': Variable("__private_var"),
        'one_underscore': Variable("one_underscore"),
        'two__underscores__here': Variable("two__underscores__here"),
        # ----- Sets:
        ' {} ': Set(),
        '{{}, {}}': Set(Set(), Set()),
        '{1,000, 3.05}': Set(Number(1000), Number(3.05)),
        '{1,234,567}': Set(Number(1234567)),
        '{23,24,25}': Set(Number(23), Number(24), Number(25)),
        '{100, 200, 300}': Set(Number(100), Number(200), Number(300)),
        '{var1, var2}': Set(Variable("var1"), Variable("var2")),
        '{var, "string"}': Set(Variable("var"), String("string")),
        '{3, var, "string"}': Set(Number(3), String("string"), Variable("var")),
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
        # Invalid whatever:
        "-",
        "this is definitely not an operand",
    )


class TestTranslations(object):
    
    grammar = GenericGrammar()
    
    strings = {
        'hola amigos': '"hola amigos"',
        'arepa': '"arepa"',
        '2': '"2"',
    }
    
    numbers = {
        4: "4",
        4.0: "4",
        4.3: "4.3",
        3.20: "3.2",
    }
    
    def test_string(self):
        for (original, translation) in self.strings.items():
            representation = self.grammar.represent_operand(String(original))
            eq_(representation, translation)
    
    def test_number(self):
        for (original, translation) in self.numbers.items():
            representation = self.grammar.represent_operand(Number(original))
            eq_(representation, translation)

