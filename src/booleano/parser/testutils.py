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

from booleano.parser.generic import EvaluableParser, ConvertibleParser

__all__ = ["BaseParseTest"]


class BaseParseTest(object):
    """
    The base test case for the parser of a grammar.
    
    Subclasses must define all the following attributes for the test case to
    work.
    
    .. attribute:: grammar
    
        An instance of the grammar to be tested.
    
    .. attribute:: namespace
    
        An instance of the namespace to be used.
    
    .. attribute:: expressions
    
        A dictionary with all the valid expressions recognized by the grammar,
        where each key is the expression itself and its item is the mock
        representation of the operation.
    
    """
    
    def __init__(self, *args, **kwargs):
        super(BaseParseTest, self).__init__(*args, **kwargs)
        self.evaluable_parser = EvaluableParser(self.grammar, self.namespace)
        self.convertible_parser = ConvertibleParser(self.grammar,
                                                    self.namespace)
        # Because the grammar in both parsers is the exact same thing (the
        # only thing that changes are a couple of parse actions), we're going
        # to select one of them to represent the parsers when the post-parse
        # actions are not relevant -- I've selected the evaluable one
        # arbitrarily:
        self.parser = self.evaluable_parser
    
    def test_infinitely_recursive_constructs(self):
        """
        There must not exist infinitely recursive constructs in the grammar
        built by the parser.
        
        """
        # Building the parser:
        self.evaluable_parser.build_parser()
        self.convertible_parser.build_parser()
        # Finally, validate the whole grammar:
        self.evaluable_parser._parser.validate()
        self.convertible_parser._parser.validate()
    
    def test_constant_expressions(self):
        """
        Constants expressions should be represented the same way in evaluable
        and convertible trees.
        
        """
        for expression, expected_node in self.constant_expressions.items():
            yield (check_expression, self.evaluable_parser, expression,
                   expected_node)
            yield (check_expression, self.convertible_parser, expression,
                   expected_node)
    
    def test_constant_operands(self):
        """
        Valid operands must be parsed successfully.
        
        """
        operand_parser = self.parser.define_operand().parseString
        for expression, expected_operand in self.constant_operands.items():
            
            # Making a Nose test generator:
            def check():
                node = operand_parser(expression, parseAll=True)
                eq_(1, len(node))
                expected_operand.check_equivalence(node[0])
            check.description = ('"%s" is a valid operand' % expression)
            
            yield check
    
    def test_invalid_operands(self):
        """
        Expressions representing invalid operands must not yield a parse tree.
        
        """
        operand_parser = self.parser.define_operand().parseString
        for expression in self.invalid_operands:
            
            # Making a Nose test generator:
            @raises(ParseException)
            def check():
                operand_parser(expression, parseAll=True)
            check.description = ('"%s" does NOT represent an operand' %
                                 expression)
            
            yield check


def check_expression(parser, expression, expected_node):
    """
    Check that the parse tree of ``expression`` with ``parser``, equals
    ``expected_node``.
    
    """
    tree = parser(expression)
    expected_node.check_equivalence(tree.root_node)

