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
Generic Pyparsing-based parser implementation.

"""

import re

from pyparsing import (Suppress, CaselessLiteral, Word, quotedString, alphas,
    nums, operatorPrecedence, opAssoc, Forward, ParseException, removeQuotes,
    Optional, OneOrMore, Combine, StringStart, StringEnd, ZeroOrMore, Group,
    Regex, Literal, delimitedList)

from booleano.parser.trees import EvaluableParseTree, ConvertibleParseTree
from booleano.operations import (Truth, Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset,
    String, Number, Set, Variable, Function, PlaceholderVariable,
    PlaceholderFunction)
from booleano.exc import BadExpressionError


__all__ = ("EvaluableParser", "ConvertibleParser")


class Parser(object):
    """
    Base class for parsers.
    
    """
    
    parse_tree_class = None
    
    def __init__(self, grammar):
        self._parser = None
        self._grammar = grammar
    
    def __call__(self, expression):
        """
        Parse ``expression`` and return its parse tree.
        
        :param expression: The expression to be parsed.
        :type expression: basestring
        :return: The parse tree.
        :rtype: ParseTree
        
        The parser will be built if it's not been built yet.
        
        """
        if not self._parser:
            self.build_parser()
        
        result = self._parser.parseString(expression, parseAll=True)
        root_node = result[0]
        return self.parse_tree_class(root_node)
    
    def build_parser(self):
        self._parser = (StringStart() + self.define_operation() + StringEnd())
    
    #{ Operand generators; used to create the grammar
    
    def define_operation(self):
        grp_start = Suppress(self._grammar.get_token("group_start"))
        grp_end = Suppress(self._grammar.get_token("group_end"))
        
        # Making the relational operations:
        t_eq = self._grammar.get_token("eq")
        t_ne = self._grammar.get_token("ne")
        t_lt = self._grammar.get_token("lt")
        t_gt = self._grammar.get_token("gt")
        t_le = self._grammar.get_token("le")
        t_ge = self._grammar.get_token("ge")
        eq = CaselessLiteral(t_eq)
        ne = CaselessLiteral(t_ne)
        lt = CaselessLiteral(t_lt)
        gt = CaselessLiteral(t_gt)
        le = CaselessLiteral(t_le)
        ge = CaselessLiteral(t_ge)
        relationals = eq ^ ne ^ lt ^ gt ^ le ^ ge
        # TODO: Avoid doing this:
        self.__operations__ = {
            t_eq: Equal,
            t_ne: NotEqual,
            t_lt: LessThan,
            t_gt: GreaterThan,
            t_le: LessEqual,
            t_ge: GreaterEqual,
        }
        
        # Making the logical connectives:
        not_ = CaselessLiteral(self._grammar.get_token("not"))
        and_ = Suppress(self._grammar.get_token("and"))
        in_or = CaselessLiteral(self._grammar.get_token("or"))
        ex_or = CaselessLiteral(self._grammar.get_token("xor"))
        or_ = in_or | ex_or
        
        operand = self.define_operand()
        
        operation = operatorPrecedence(
            operand,
            [
                (relationals, 2, opAssoc.LEFT, self.make_relational),
                #(not_, 1, opAssoc.RIGHT),
                (and_, 2, opAssoc.LEFT, self.make_and),
                (or_, 2, opAssoc.LEFT),
            ]
        )
        
        return operation
    
    def define_operand(self):
        """
        Return the syntax definition for an operand.
        
        An operand can be a variable, a string, a number or a set. A set
        is made of other operands, including other sets.
        
        **This method shouldn't be overridden**. Instead, override the syntax
        definitions for variables, strings and/or numbers.
        
        If you want to customize the sets, check :meth:`T_SET_START`,
        :meth:`T_SET_END` and :meth:`T_ELEMENT_SEPARATOR`.
        
        """
        identifier = self.define_identifier()
        operand = Forward()
        
        # Defining the sets:
        set_start = Suppress(self._grammar.get_token("set_start"))
        set_end = Suppress(self._grammar.get_token("set_end"))
        element_separator = self._grammar.get_token("element_separator")
        elements = delimitedList(operand, delim=element_separator)
        set_ = Group(set_start + Optional(elements) + set_end)
        set_.setParseAction(self.make_set)
        set_.setName("set")
        
        # Defining the variables:
        variable = identifier.copy()
        variable.setName("variable")
        variable.addParseAction(self.make_variable)
        
        # Defining the functions:
        function_name = identifier.copy()
        function_name = function_name.setResultsName("function_name")
        function_name.setName("function_name")
        args_start = Suppress(self._grammar.get_token("arguments_start"))
        args_end = Suppress(self._grammar.get_token("arguments_end"))
        args_sep = self._grammar.get_token("arguments_separator")
        arguments = Optional(Group(delimitedList(operand, delim=args_sep)),
                             default=())
        arguments = arguments.setResultsName("arguments")
        function = Group(function_name + args_start + arguments + args_end)
        function.setName("function")
        function.setParseAction(self.make_function)
        
        operand << (function | variable | self.define_number() | \
                    self.define_string() | set_)
        
        return operand
    
    def define_string(self):
        """
        Return the syntax definition for a string.
        
        **Do not override this method**, it's not necessary: it already
        supports unicode strings. If you want to override the delimiters,
        check :attr:`T_QUOTES`.
        
        """
        string = quotedString.setParseAction(removeQuotes, self.make_string)
        string.setName("string")
        return string
    
    def define_number(self):
        """
        Return the syntax definition for a number in Arabic Numerals.
        
        Override this method to support numeral systems other than Arabic
        Numerals (0-9).
        
        Do not override this method just to change the character used to
        separate thousands and decimals: Use :attr:`T_THOUSANDS_SEPARATOR`
        and :attr:`T_DECIMAL_SEPARATOR`, respectively.
        
        """
        # Defining the basic tokens:
        to_dot = lambda t: "."
        to_plus = lambda t: "+"
        to_minus = lambda t: "-"
        positive_sign = Literal(self._grammar.get_token("positive_sign"))
        positive_sign.setParseAction(to_plus)
        negative_sign = Literal(self._grammar.get_token("negative_sign"))
        negative_sign.setParseAction(to_minus)
        decimal_sep = Literal(self._grammar.get_token("decimal_separator"))
        decimal_sep.setParseAction(to_dot)
        thousands_sep = Suppress(self._grammar.get_token("thousands_separator"))
        digits = Word(nums)
        # Building the integers and decimals:
        sign = positive_sign | negative_sign
        thousands = Word(nums, max=3) + \
                    OneOrMore(thousands_sep + Word(nums, exact=3))
        integers = thousands | digits
        decimals = decimal_sep + digits
        number = Combine(Optional(sign) + integers + Optional(decimals))
        number.setParseAction(self.make_number)
        number.setName("number")
        return number
    
    def define_identifier(self):
        """
        Return the syntax definition for an identifier.
        
        """
        # Defining the individual identifiers:
        def first_not_a_number(tokens):
            if tokens[0][0].isdigit():
                raise ParseException('"%s" must not start by a number for it '
                                     'to be an identifier' % tokens[0])
        space_char = re.escape(self._grammar.get_token("identifier_spacing"))
        identifier0 = Regex("[\w%s]+" % space_char, re.UNICODE)
        identifier0.setParseAction(first_not_a_number)
        identifier0.setName("individual_identifier")
        
        # Now let's include the full identifier definition, which includes
        # namespaces:
        namespace_sep = Suppress(self._grammar.get_token("namespace_separator"))
        namespace = Group(ZeroOrMore(identifier0 + namespace_sep))
        namespace.setName("namespace")
        
        # Finally, let's build the full identifier, which could have a
        # namespace:
        identifier = (namespace.setResultsName("namespace_parts") +
                      identifier0.setResultsName("identifier"))
        identifier.setName("full_identifier")
        
        return identifier
    
    #{ Pyparsing post-parse actions
    
    def make_string(self, tokens):
        """Make a String constant using the token passed."""
        return String(tokens[0])
    
    def make_number(self, tokens):
        """Make a Number constant using the token passed."""
        return Number(tokens[0])
    
    def make_variable(self, tokens):
        """Make a variable using the token passed."""
        raise NotImplementedError("It's up to the actual parser to make "
                                  "the variables")
    
    def make_function(self, tokens):
        """Make a function using the token passed."""
        raise NotImplementedError("It's up to the actual parser to make "
                                  "the functions")
    
    def make_set(self, tokens):
        """Make a Set using the token passed."""
        return Set(*tokens[0])
    
    def make_relational(self, tokens):
        """Make a relational operation using the tokens passed."""
        left_op = tokens[0][0]
        operator = tokens[0][1]
        right_op = tokens[0][2]
        
        operation = self.__operations__[operator]
        
        return operation(left_op, right_op)
    
    def make_and(self, tokens):
        """Make an *And* connective using the tokens passed."""
        return self.__make_binary_connective__(And, tokens[0])
    
    def __make_binary_connective__(self, operation_class, operands):
        """
        Return an operation represented by the binary connective 
        ``operation_class`` and its ``operands``.
        
        """
        if len(operands) == 2:
            operation = operation_class(operands[0], operands[1])
        else:
            # We're going to build the operation from right to left, so it
            # can be evaluated from left to right (a LIFO approach).
            operation = operation_class(operands[-2], operands[-1])
            operands = operands[:-2]
            operands.reverse()
            for operand in operands:
                operation = operation_class(operand, operation)
        
        return operation
    
    #}


class EvaluableParser(Parser):
    """
    Evaluable parser.
    
    """
    
    parse_tree_class = EvaluableParseTree
    
    def __init__(self, grammar, namespace):
        self._namespace = namespace
        super(EvaluableParser, self).__init__(grammar)
    
    def make_variable(self, tokens):
        """Make a Variable using the token passed."""
        var = self._namespace.get_object(tokens[1], tokens[0])
        # TODO: Check that it's a variable!!!
        return var
    
    def make_function(self, tokens):
        """Make a Function using the token passed."""
        func = self._namespace.get_object(tokens[1], tokens[0])
        # TODO: Check that it's a function!!!
        return func


class ConvertibleParser(Parser):
    """
    Convertible parser.
    
    """
    
    parse_tree_class = ConvertibleParseTree
    
    def make_variable(self, tokens):
        """Make a Placeholder variable using the token passed."""
        return PlaceholderVariable(tokens.identifier, tokens.namespace_parts)
    
    def make_function(self, tokens):
        """Make a Placeholder function using the token passed."""
        tokens = tokens[0]
        return PlaceholderFunction(tokens.identifier, tokens.namespace_parts,
                                   *tokens.arguments[0])

