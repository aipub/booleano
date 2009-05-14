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
Tests for the parser.

"""
# TODO: Move this into booleano.parser.

from nose.tools import eq_, ok_, raises
from pyparsing import ParseException


class BaseParseTest(object):
    
    def test_infinitely_recursive_constructs(self):
        """There must not exist infinitely recursive constructs."""
        self.grammar.define_string().validate()
        self.grammar.define_number().validate()
        self.grammar.define_variable().validate()
        self.grammar.define_set().validate()
        # Validating all the operands together:
        self.grammar.define_unit_operand().validate()
        # Finally, validate the whole grammar:
        self.grammar.grammar.validate()
    
    def test_valid_expressions(self):
        for expression, expected_parse_tree in self.expressions.items():
            yield (check_expression, self.grammar, expression,
                   expected_parse_tree)
    
    def test_unit_operands_alone(self):
        operand_parser = self.grammar.define_unit_operand().parseString
        for expression, expected_parse_tree in self.valid_operands.items():
            yield (check_operand, operand_parser, expression,
                   expected_parse_tree)
        for expression in self.invalid_operands:
            yield (check_invalid_operand, operand_parser, expression)


def check_expression(parser, expression, expected_parse_tree):
    parse_tree = parser(expression)
    expected_parse_tree.equals(parse_tree)


def check_operand(parser, expression, expected_parse_tree):
    parse_tree = parser(expression, parseAll=True)
    eq_(1, len(parse_tree))
    expected_parse_tree.equals(parse_tree[0])


@raises(ParseException)
def check_invalid_operand(parser, expression):
    parser(expression, parseAll=True)
