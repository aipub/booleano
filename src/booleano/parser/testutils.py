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
Semi-automatic utilities to test Booleano grammars and parsers.

"""
from nose.tools import eq_, ok_, raises
from pyparsing import ParseException

from booleano.parser.parsers import Parser, EvaluableParser, ConvertibleParser

__all__ = ("BaseGrammarTest", )


class BaseGrammarTest(object):
    """
    Base test case for a grammar and the expressions its parser could handle.
    
    Subclasses must define all the following attributes for the test case to
    work.
    
    .. attribute:: grammar
        
        An instance of the grammar to be tested. **This attribute must be set
        in the subclasses**, like this::
        
            from booleano.parser import Grammar
            
            class TestMyGrammar(BaseGrammarTest):
            
                grammar = Grammar(ne="<>")
    
        :type: :class:`booleano.parser.Grammar`
    
    .. attribute:: expressions
    
        A dictionary with all the valid expressions recognized by the grammar,
        where each key is the expression itself and its item is the mock
        representation of the operation.
        
        :type: dict
    
    .. attribute:: badformed_expressions
    
        A list of expressions that are bad-formed in the :attr:`grammar`.
        
        :type: list
    
    .. attribute:: single_operands
    
        A dictionary where the key is an expression that contains a single
        operand (i.e., no operator) and the item is the :term:`root node` of the
        expected :term:`parse tree`.
        
        :type: dict
    
    .. attribute:: invalid_operands
    
        A list of expressions which contain a single operand and it is invalid.
        
        :type: list
    
    """
    
    def __init__(self, *args, **kwargs):
        super(BaseGrammarTest, self).__init__(*args, **kwargs)
        # Let's use the convertible parser to ease testing:
        self.parser = ConvertibleParser(self.grammar)
    
    def test_expressions(self):
        """Valid expressions should yield the expected parse tree."""
        for expression, expected_node in self.expressions.items():
            
            # Making a Nose test generator:
            def check():
                tree = self.parser(expression)
                expected_node.check_equivalence(tree.root_node)
            check.description = 'Operation "%s" should yield "%s"' % \
                                (expression, expected_node)
            
            yield check
    
    def test_badformed_expressions(self):
        """Expressions with an invalid syntax must not yield a parse tree."""
        for expression in self.badformed_expressions:
            
            # Making a Nose test generator:
            @raises(ParseException)
            def check():
                self.parser(expression)
            check.description = "'%s' is an invalid expression" % expression
            
            yield check
    
    def test_single_operands(self):
        """
        Expressions made up of a single operand must yield the expected operand.
        
        """
        operand_parser = self.parser.define_operand().parseString
        
        for expression, expected_operand in self.single_operands.items():
            
            # Making a Nose test generator:
            def check():
                node = operand_parser(expression, parseAll=True)
                eq_(1, len(node))
                expected_operand.check_equivalence(node[0])
            check.description = ('Single operand "%s" should return %s' %
                                 (expression, expected_operand))
            
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
            check.description = ('"%s" is an invalid operand' %
                                 expression)
            
            yield check

