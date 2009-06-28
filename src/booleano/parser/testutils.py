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
Utilities to test Booleano grammars.

"""
from nose.tools import eq_, ok_, raises
from pyparsing import ParseException

__all__ = ["BaseParseTest"]


class BaseParseTest(object):
    """
    The base test case for the parser of a grammar.
    
    Subclasses must define all the following attributes for the test case to
    work.
    
    .. attribute:: grammar
    
        An instance of the grammar to be tested.
    
    .. attribute:: expressions
    
        A dictionary with all the valid expressions recognized by the grammar,
        where each key is the expression itself and its item is the mock
        representation of the operation.
    
    """
    
    def test_infinitely_recursive_constructs(self):
        """
        There must not exist infinitely recursive constructs in the grammar.
        
        """
        self.grammar.define_string().validate()
        self.grammar.define_number().validate()
        self.grammar.define_name().validate()
        # Validating all the operands together, including sets:
        self.grammar.define_operand(True).validate()
        self.grammar.define_operand(False).validate()
        # Finally, validate the whole grammar:
        self.grammar.evaluable_grammar.validate()
        self.grammar.convertible_grammar.validate()
    
    def test_contant_expressions(self):
        """
        Contants expressions should be represented the same way in evaluable
        and convertible trees.
        
        """
        for expression, expected_node in self.constant_expressions.items():
            yield (check_expression, self.grammar.parse_evaluable, expression,
                   expected_node)
            yield (check_expression, self.grammar.parse_convertible, expression,
                   expected_node)
    
    def test_constant_operands(self):
        operand_parser = self.grammar.define_operand().parseString
        for expression, expected_node in self.constant_operands.items():
            yield (check_operand, operand_parser, expression,
                   expected_node)
    
    def test_invalid_operands(self):
        operand_parser = self.grammar.define_operand().parseString
        for expression in self.invalid_operands:
            yield (check_invalid_operand, operand_parser, expression)


def check_expression(parser, expression, expected_node):
    tree = parser(expression)
    expected_node.check_equivalence(tree.root_node)


def check_operand(parser, expression, expected_node):
    node = parser(expression, parseAll=True)
    eq_(1, len(node))
    expected_node.check_equivalence(node[0])


@raises(ParseException)
def check_invalid_operand(parser, expression):
    parser(expression, parseAll=True)

