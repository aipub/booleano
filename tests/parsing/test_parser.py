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

from booleano.parser.generic import Grammar
from booleano.parser.scope import Namespace
from booleano.parser.testutils import BaseParseTest
from booleano.operations import (Truth, Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset,
    String, Number, Set, Variable, Function, VariablePlaceholder,
    FunctionPlaceholder)


class TestParsing(BaseParseTest):
    """
    Tests for the parser of the generic grammar.
    
    """
    grammar = Grammar()
    
    namespace = Namespace(
        # Global objects:
        {
            
        },
        # Sub-namespaces
        {}
    )
    
    # Literals-only expressions:
    literal_expressions = {
        '  "a string" == 245    ': Equal(String("a string"), Number(245)),
        '   2 > 5   ': GreaterThan(Number(2), Number(5)),
    }
    
    # Expressions whose variables and functions are going to be evaluated:
    # TODO:
    evaluable_expressions = {
    }
    
    # Expressions whose variables and functions are going to be converted:
    convertible_expressions = {
        ' last_night': VariablePlaceholder("last_night", None),
    }
    
    literals = {
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
    }
    
    # TODO:
    evaluable_operands = {}
    
    convertible_operands = {
        # ----- Variables:
        'today': VariablePlaceholder("today", None),
        'camelCase': VariablePlaceholder("camelCase", None),
        'with_underscore': VariablePlaceholder("with_underscore", None),
        ' v1 ': VariablePlaceholder("v1", None),
        'var1_here': VariablePlaceholder("var1_here", None),
        u'résumé': VariablePlaceholder(u"résumé", None),
        u'有容乃大': VariablePlaceholder(u"有容乃大", None),
        '    spaces': VariablePlaceholder("spaces", None),
        'spaces    ': VariablePlaceholder("spaces", None),
        '  spaces  ': VariablePlaceholder("spaces", None),
        '_protected_var': VariablePlaceholder("_protected_var", None),
        '__private_var': VariablePlaceholder("__private_var", None),
        'one_underscore': VariablePlaceholder("one_underscore", None),
        'two__underscores__here': VariablePlaceholder("two__underscores__here",
                                                      None),
        'case_insensitive_var': VariablePlaceholder("CASE_INSENSITIVE_VAR", 
                                                    None),
        'CASE_INSENSITIVE_VAR': VariablePlaceholder("case_insensitive_var", 
                                                    None),
        'cAsE_iNsEnSiTiVe_VaR': VariablePlaceholder("CaSe_InSeNsItIvE_vAr", 
                                                    None),
        u'MAYÚSCULA_minúscula': VariablePlaceholder(u"mayúscula_MINÚSCULA", 
                                                    None),
        # ----- Sets:
        '{var1, var2}': Set(VariablePlaceholder("var1", None),
                            VariablePlaceholder("var2", None)),
        '{var, "string"}': Set(VariablePlaceholder("var", None), 
                               String("string")),
        '{3, var, "string"}': Set(Number(3), String("string"),
                                  VariablePlaceholder("var", None)),
    }
    
    invalid_literals = (
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

