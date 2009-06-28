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
Syntax localizations for the boolean expressions.

This module contains the generic grammar, which uses mathematical symbols only
and no words.

"""
import re

from pyparsing import (Suppress, CaselessLiteral, Word, quotedString, alphas,
    nums, operatorPrecedence, opAssoc, Forward, ParseException, removeQuotes,
    Optional, OneOrMore, Combine, StringStart, StringEnd, ZeroOrMore, Group,
    Regex, Literal, delimitedList)

from booleano.parser.trees import EvaluableParseTree, ConvertibleParseTree
from booleano.operations import (Truth, Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, Contains, IsSubset,
    String, Number, Set, Variable, Function, VariablePlaceholder,
    FunctionPlaceholder)


__all__ = ["GenericGrammar"]


class _GrammarMeta(type):
    """
    Complete a grammar right after the basic settings have been defined.
    
    This is the meta class for the grammars, which will build each grammar
    once the individual tokens are defined.
    
    """
    
    def __init__(cls, name, bases, ns):
        tokens = cls.__dict__.copy()
        tokens.update(ns)
        
        grp_start = Suppress(tokens['T_GROUP_START'])
        grp_end = Suppress(tokens['T_GROUP_END'])
        
        # Making the relational operations:
        eq = CaselessLiteral(tokens['T_EQ'])
        ne = CaselessLiteral(tokens['T_NE'])
        lt = CaselessLiteral(tokens['T_LT'])
        gt = CaselessLiteral(tokens['T_GT'])
        le = CaselessLiteral(tokens['T_LE'])
        ge = CaselessLiteral(tokens['T_GE'])
        relationals = eq | ne | lt | gt | le | ge
        cls.__operations__ = {
            tokens['T_EQ']: Equal,
            tokens['T_NE']: NotEqual,
            tokens['T_LT']: LessThan,
            tokens['T_GT']: GreaterThan,
            tokens['T_LE']: LessEqual,
            tokens['T_GE']: GreaterEqual,
        }
        
        # Making the logical connectives:
        not_ = CaselessLiteral(tokens['T_NOT'])
        and_ = CaselessLiteral(tokens['T_AND'])
        in_or = CaselessLiteral(tokens['T_OR'])
        ex_or = CaselessLiteral(tokens['T_XOR'])
        or_ = in_or | ex_or
        
        # TODO: There might be a better way to change the parse action
        # on-the-fly. Gotta ask in the Pyparsing mailing list.
        evaluable_operand = cls.define_operand()
        convertible_operand = cls.define_operand(False)
        
        evaluable_grammar = operatorPrecedence(
            evaluable_operand,
            [
                (relationals, 2, opAssoc.LEFT, cls.make_relational),
                #(not_, 1, opAssoc.RIGHT),
                (and_, 2, opAssoc.LEFT),
                (or_, 2, opAssoc.LEFT),
            ]
        )
        
        convertible_grammar = operatorPrecedence(
            convertible_operand,
            [
                (relationals, 2, opAssoc.LEFT, cls.make_relational),
                #(not_, 1, opAssoc.RIGHT),
                (and_, 2, opAssoc.LEFT),
                (or_, 2, opAssoc.LEFT),
            ]
        )
        
        cls.evaluable_grammar = StringStart() + evaluable_grammar + StringEnd()
        cls.convertible_grammar = (StringStart() + convertible_grammar +
                                   StringEnd())


class GenericGrammar(object):
    
    __metaclass__ = _GrammarMeta
    
    locale = "xx"
    
    #{ Default tokens/operators.
    
    # Some logical connectives:
    T_NOT = "~"
    T_AND = "&"
    T_OR = "|"
    T_XOR = "^"
    
    # Relational operators:
    T_EQ = "=="
    T_NE = "!="
    T_LT = "<"
    T_GT = ">"
    T_LE = "<="
    T_GE = ">="
    
    # Set operators:
    T_IN = u"∈"
    T_CONTAINED = u"⊂"
    T_SET_START = "{"
    T_SET_END = "}"
    T_ELEMENT_SEPARATOR = ","
    
    # Grouping marks:
    T_STRING_START = '"'
    T_STRING_END = '"'
    T_GROUP_START = "("
    T_GROUP_END = ")"
    
    # Marks related to function arguments:
    T_ARGUMENTS_START = "("
    T_ARGUMENTS_END = ")"
    T_ARGUMENTS_SEPARATOR = ","
    
    # Signed numbers:
    T_POSITIVE_SIGN = "+"
    T_NEGATIVE_SIGN = "-"
    
    # Miscellaneous tokens:
    T_NAME_SPACING = "_"
    T_DECIMAL_SEPARATOR = "."
    T_THOUSANDS_SEPARATOR = ","
    
    def __init__(self, variables={}, var_containers={}, functions={}):
        self.variables = variables
        self.var_containers = var_containers
        self.functions = functions
    
    def parse_evaluable(self, expression):
        """
        Parse ``expression`` and turn its truth-evaluable parse tree.
        
        :param expression: The expression to be parsed.
        :type expression: basestring
        :return: The truth-evaluable parse tree.
        :rtype: EvaluableParseTree
        
        """
        result = self.evaluable_grammar.parseString(expression, parseAll=True)
        root_node = result[0]
        return EvaluableParseTree(root_node)
    
    def parse_convertible(self, expression):
        result = self.convertible_grammar.parseString(expression, parseAll=True)
        root_node = result[0]
        return ConvertibleParseTree(root_node)
    
    def __call__(self, expression):
        """
        Parse ``expression`` and return its parse tree.
        
        """
        node = self.evaluable_grammar.parseString(expression, parseAll=True)
        return node[0]
    
    #{ Operand generators; used to create the grammar
    
    @classmethod
    def define_operand(cls, evaluable=True):
        """
        Return the syntax definition for an operand.
        
        :param evaluable: Whether the variables and functions should be
            truth-evaluable; otherwise, they'll be placeholders.
        
        An operand can be a variable, a string, a number or a set. A set
        is made of other operands, including other sets.
        
        **This method shouldn't be overridden**. Instead, override the syntax
        definitions for variables, strings and/or numbers.
        
        If you want to customize the sets, check :meth:`T_SET_START`,
        :meth:`T_SET_END` and :meth:`T_ELEMENT_SEPARATOR`.
        
        """
        object_name = cls.define_name()
        operand = Forward()
        
        # Defining the sets:
        set_start = Suppress(cls.T_SET_START)
        set_end = Suppress(cls.T_SET_END)
        elements = delimitedList(operand, delim=cls.T_ELEMENT_SEPARATOR)
        set_ = Group(set_start + Optional(elements) + set_end)
        set_.setParseAction(cls.make_set)
        set_.setName("set")
        
        # Defining the variables:
        variable = object_name.setName("variable")
        
        # Defining the functions:
        function_name = object_name.setName("function_name")
        args_start = Suppress(cls.T_ARGUMENTS_START)
        args_end = Suppress(cls.T_ARGUMENTS_END)
        args_sep = cls.T_ARGUMENTS_SEPARATOR
        arguments = Optional(delimitedList(operand, delim=args_sep))
        function = Group(function_name + args_start + arguments + args_end)
        
        # Turning the variables and functions into evaluable or placeholder
        # operands:
        if evaluable:
            variable.addParseAction(cls.make_variable)
            function.setParseAction(cls.make_function)
        else:
            variable.addParseAction(cls.make_variable_placeholder)
            function.setParseAction(cls.make_function_placeholder)
        
        operand << (variable | cls.define_number() | \
                    cls.define_string() | set_)
        
        return operand
    
    @classmethod
    def define_string(cls):
        """
        Return the syntax definition for a string.
        
        **Do not override this method**, it's not necessary: it already
        supports unicode strings. If you want to override the delimiters,
        check :attr:`T_QUOTES`.
        
        """
        string = quotedString.setParseAction(removeQuotes, cls.make_string)
        string.setName("string")
        return string
    
    @classmethod
    def define_number(cls):
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
        positive_sign = Literal(cls.T_POSITIVE_SIGN).setParseAction(to_plus)
        negative_sign = Literal(cls.T_NEGATIVE_SIGN).setParseAction(to_minus)
        decimal_sep = Literal(cls.T_DECIMAL_SEPARATOR).setParseAction(to_dot)
        thousands_sep = Suppress(cls.T_THOUSANDS_SEPARATOR)
        digits = Word(nums)
        # Building the integers and decimals:
        sign = positive_sign | negative_sign
        thousands = Word(nums, max=3) + \
                    OneOrMore(thousands_sep + Word(nums, exact=3))
        integers = thousands | digits
        decimals = decimal_sep + digits
        number = Combine(Optional(sign) + integers + Optional(decimals))
        number.setParseAction(cls.make_number)
        number.setName("number")
        return number
    
    @classmethod
    def define_name(cls):
        """
        Return the syntax definition for an object name.
        
        """
        def first_not_a_number(tokens):
            if tokens[0][0].isdigit():
                raise ParseException('"%s" must not start by a number for it '
                                     'to be an object name' % tokens[0])
        space_char = re.escape(cls.T_NAME_SPACING)
        object_name = Regex("[\w%s]+" % space_char, re.UNICODE)
        object_name.setParseAction(first_not_a_number)
        object_name.setName("object")
        return object_name
    
    #{ Parse actions
    
    @classmethod
    def make_string(cls, tokens):
        """Make a String constant using the token passed."""
        return String(tokens[0])
    
    @classmethod
    def make_number(cls, tokens):
        """Make a Number constant using the token passed."""
        return Number(tokens[0])
    
    @classmethod
    def make_variable(cls, tokens):
        """Make a Variable using the token passed."""
        return Variable(tokens[0])
    
    @classmethod
    def make_variable_placeholder(cls, tokens):
        """Make a Variable placeholder using the token passed."""
        return VariablePlaceholder(tokens[0])
    
    @classmethod
    def make_function(cls, tokens):
        """Make a Function using the token passed."""
        return Function(tokens[0])
    
    @classmethod
    def make_function_placeholder(cls, tokens):
        """Make a Function placeholder using the token passed."""
        return FunctionPlaceholder(tokens[0])
    
    @classmethod
    def make_set(cls, tokens):
        """Make a Set using the token passed."""
        return Set(*tokens[0])
    
    @classmethod
    def make_relational(cls, tokens):
        """Make a relational operation using the tokens passed."""
        left_op = tokens[0][0]
        operator = tokens[0][1]
        right_op = tokens[0][2]
        
        operation = cls.__operations__[operator]
        
        return operation(left_op, right_op)
    
    #}

