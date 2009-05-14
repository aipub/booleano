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
Test suite for the generic grammar parser.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises
from pyparsing import ParseException

from booleano.parser import GenericGrammar
from booleano.operations.operators import (FunctionOperator, TruthOperator,
        NotOperator, AndOperator, OrOperator, XorOperator, EqualityOperator,
        LessThanOperator, GreaterThanOperator, LessEqualOperator, 
        GreaterEqualOperator, ContainsOperator, SubsetOperator)
from booleano.operations.operands import (String, Number, Set, Variable)

from tests.parsing import BaseParseTest
from tests.parsing.mock_operations import STRING, NUMBER, VARIABLE, SET


class TestValidExpressions(BaseParseTest):
    grammar = GenericGrammar()
    
    expressions = {
        '  "a string"     ': STRING("a string"),
        '   2   ': NUMBER(2),
        ' last_night': VARIABLE("last_night"),
        }
    
    valid_operands = {
        # ----- Strings
        '"oneword"': STRING("oneword"),
        '"double quotes"': STRING("double quotes"),
        "'single quotes'": STRING("single quotes"),
        "''": STRING(""),
        "'something with \"quotes\"'": STRING('something with "quotes"'),
        '"something with \'quotes\'"': STRING("something with 'quotes'"),
        u'"áéíóúñçÁÉÍÓÚÑÇ"': STRING(u"áéíóúñçÁÉÍÓÚÑÇ"),
        u'"海納百川，有容乃大"': STRING(u"海納百川，有容乃大"),
        u"'مقالة مختارة'": STRING(u"مقالة مختارة"),
        u'"вільної енциклопедії"': STRING(u"вільної енциклопедії"),
        # ----- Numbers
        '1': NUMBER(1),
        '01': NUMBER(1),
        '5000': NUMBER(5000),
        '2.34': NUMBER(2.34),
        '2.2': NUMBER(2.2),
        '5,000': NUMBER(5000),
        '1,000,000.34': NUMBER(1000000.34),
        # ----- Variables:
        'today': VARIABLE("today"),
        'camelCase': VARIABLE("camelCase"),
        'with_underscore': VARIABLE("with_underscore"),
        u'résumé': VARIABLE(u"résumé"),
        u'有容乃大': VARIABLE(u"有容乃大"),
        '    spaces': VARIABLE("spaces"),
        'spaces    ': VARIABLE("spaces"),
        '  spaces  ': VARIABLE("spaces"),
        '_protected_var': VARIABLE("_protected_var"),
        '__private_var': VARIABLE("__private_var"),
        'one_underscore': VARIABLE("one_underscore"),
        'two__underscores__here': VARIABLE("two__underscores__here"),
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
        # Invalid whatever:
        "this is a phrase, not an operand",
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

