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
Parser for boolean expressions.

These expressions can be written using mathematical symbols or in a natural
language.

"""
import re

from pyparsing import (Suppress, CaselessLiteral, Word, quotedString, alphas,
                       nums, operatorPrecedence, opAssoc, Forward,
                       ParseException, removeQuotes, Optional, OneOrMore,
                       Combine, StringStart, StringEnd, ZeroOrMore, Group,
                       Regex, Literal, delimitedList)

from booleano.operations.operators import (FunctionOperator, TruthOperator,
        NotOperator, AndOperator, OrOperator, XorOperator, EqualityOperator,
        LessThanOperator, GreaterThanOperator, LessEqualOperator, 
        GreaterEqualOperator, ContainsOperator, SubsetOperator)
from booleano.operations.operands import String, Number, Set, Variable


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
        
        # Making the logical connectives:
        not_ = CaselessLiteral(tokens['T_NOT'])
        and_ = CaselessLiteral(tokens['T_AND'])
        in_or = CaselessLiteral(tokens['T_OR'])
        ex_or = CaselessLiteral(tokens['T_XOR'])
        or_ = in_or | ex_or
        
        operand = cls.define_unit_operand() | cls.define_set()
        
        grammar = operatorPrecedence(
            operand,
            [
                (relationals, 2, opAssoc.LEFT),
                #(not_, 1, opAssoc.RIGHT),
                (and_, 2, opAssoc.LEFT),
                (or_, 2, opAssoc.LEFT),
            ]
        )
        
        cls.grammar = StringStart() + grammar + StringEnd()


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
    
    # Miscellaneous tokens:
    T_VARIABLE_SPACING = "_"
    T_DECIMAL_SEPARATOR = "."
    T_THOUSANDS_SEPARATOR = ","
    
    def __init__(self, variables={}, var_containers={}, functions={}):
        self.variables = variables
        self.var_containers = var_containers
        self.functions = functions
    
    def __call__(self, expression):
        """
        Parse ``expression`` and return its parse tree.
        
        """
        parse_tree = self.grammar.parseString(expression)
        return parse_tree[0]
    
    #{ Operand generators; used to create the grammar
    
    @classmethod
    def define_unit_operand(cls):
        """
        Return the syntax definition for a unit operand.
        
        A "unit operand" can be a variable, a string or a number.
        
        **This method shouldn't be overridden**. Instead, override the syntax
        definitions for variables, strings and/or numbers.
        
        """
        operand = cls.define_number() | cls.define_string() | \
                  cls.define_variable()
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
        decimal_sep = Literal(cls.T_DECIMAL_SEPARATOR).setParseAction(to_dot)
        thousands_sep = Suppress(cls.T_THOUSANDS_SEPARATOR)
        digits = Word(nums)
        # Building the integers and decimals:
        thousands = Word(nums, max=3) + \
                    OneOrMore(thousands_sep + Word(nums, exact=3))
        integers = thousands | digits
        decimals = decimal_sep + OneOrMore(digits)
        number = Combine(integers + Optional(decimals))
        number.setParseAction(cls.make_number)
        number.setName("number")
        return number
    
    @classmethod
    def define_variable(cls):
        """
        Return the syntax definition for a variable.
        
        """
        space_char = re.escape(cls.T_VARIABLE_SPACING)
        variable = Regex("[\w%s]+" % space_char, re.UNICODE)
        variable.setParseAction(cls.make_variable)
        variable.setName("variable")
        return variable
    
    @classmethod
    def define_set(cls):
        """
        Return the syntax definition for a set.
        
        """
        set_ = Forward()
        
        set_start = Suppress(cls.T_SET_START)
        set_end = Suppress(cls.T_SET_END)
        element = cls.define_unit_operand() | set_
        elements = delimitedList(element, cls.T_ELEMENT_SEPARATOR)
        
        set_ << set_start + Group(Optional(elements)) + set_end
        
        return set_
    
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
    
    #{ Translators
    
    def represent_operand(self, operand):
        """
        Return the string representation of ``operand``.
        
        :param operand: The operand to be represented as a string.
        :type operand: :class:`booleano.operations.operands.Operand`
        :return: ``operand`` as a string.
        :rtype: unicode
        
        """
        if isinstance(operand, String):
            return self.represent_string(operand.constant_value)
        if isinstance(operand, Number):
            return self.represent_number(operand.constant_value)
    
    def represent_string(self, string):
        """
        Return ``string`` as a string quoted with ``T_STRING_START`` and
        ``T_STRING_END``.
        
        """
        return u'%s%s%s' % (self.T_STRING_START, string, self.T_STRING_END)
    
    def represent_number(self, number):
        """
        Return float ``number`` as a string and remove the decimals if it's
        an integer.
        
        """
        if not hasattr(number, "is_integer") or number.is_integer():
            number = int(number)
        return str(number)
    
    #}

