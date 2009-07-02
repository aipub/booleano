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

The grammar supported by these parsers doesn't use words, but mathematical
symbols for the operators.

"""
import re

from pyparsing import (Suppress, CaselessLiteral, Word, quotedString, alphas,
    nums, operatorPrecedence, opAssoc, Forward, ParseException, removeQuotes,
    Optional, OneOrMore, Combine, StringStart, StringEnd, ZeroOrMore, Group,
    Regex, Literal, delimitedList)

from booleano.parser.trees import EvaluableParseTree, ConvertibleParseTree
from booleano.operations import (Truth, Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset,
    String, Number, Set, Variable, Function, VariablePlaceholder,
    FunctionPlaceholder)
from booleano.exc import GrammarError, BadExpressionError


__all__ = ("Grammar", "EvaluableParser", "ConvertibleParser")


class Grammar(object):
    """
    Adaptive grammar.
    
    Instances of this class contain the properties of the grammar, but are not
    able to generate a parser based on the represented grammar -- that is
    a :class:`Parser`'s job.
    
    """
    
    default_tokens = {
        # Some logical connectives:
        'not': "~",
        'and': "&",
        'or': "|",
        'xor': "^",
        # Relational operators:
        'eq': "==",
        'ne': "!=",
        'lt': "<",
        'gt': ">",
        'le': "<=",
        'ge': ">=",
        # Set operators:
        'belongs_to': u"∈",
        'is_subset': u"⊂",
        'set_start': "{",
        'set_end': "}",
        'element_separator': ",",
        # Grouping marks:
        'string_start': '"',
        'string_end': '"',
        'group_start': "(",
        'group_end': ")",
        # Marks related to function arguments:
        'arguments_start': "(",
        'arguments_end': ")",
        'arguments_separator': ",",
        # Numeric-related tokens:
        'positive_sign': "+",
        'negative_sign': "-",
        'decimal_separator': ".",
        'thousands_separator': ",",
        # Miscellaneous tokens:
        'identifier_spacing': "_",
        'namespace_separator': ":",
    }
    
    default_settings = {
        'superset_right_in_is_subset': True,
        'set_right_in_contains': True,
        'optional_positive_sign': True,
    }
    
    known_generators = set([
        "operation",
        "string",
        "number",
    ])
    
    def __init__(self, settings=None, generators=None, **tokens):
        """
        Set up a grammar, possibly customizing its properties.
        
        :param custom_settings: The grammar settings to be overridden, if any.
        :type custom_settings: dict
        :param custom_generators: The custom generators for the parser to be
            generated, if any.
        :type custom_generators: dict
        
        Keyword arguments represent the tokens to be overridden.
        
        """
        self._custom_settings = {}
        self._custom_generators = {}
        self._custom_tokens = {}
        # Setting the custom properties:
        settings = settings or {}
        generators = generators or {}
        for (setting_name, setting) in settings.items():
            self.set_setting(setting_name, setting)
        for (generator_name, generator) in generators.items():
            self.set_custom_generator(generator_name, generator)
        for (token_name, token) in tokens.items():
            self.set_token(token_name, token)
    
    #{ Token handling
    
    def get_token(self, token_name):
        """
        Return the token called ``token_name``.
        
        :param token_name: The name/key of the token to be returned.
        :type token_name: basestring
        :return: The requested token.
        :rtype: basestring
        :raises GrammarError: If the ``token_name`` is unknown.
        
        If the token doesn't have a custom value, the default value will be
        returned instead.
        
        """
        self._check_token_existence(token_name)
        return self._custom_tokens.get(token_name,
                                       self.default_tokens[token_name])
    
    def set_token(self, token_name, token):
        """
        Set the token called ``token_name`` to the custom value ``token``.
        
        :param token_name: The name of the token to be customized.
        :type token_name: basestring
        :param token: The new value of the token.
        :type token: basestring
        :raises GrammarError: If the ``token_name`` is unknown.
        
        """
        self._check_token_existence(token_name)
        self._custom_tokens[token_name] = token
    
    def _check_token_existence(self, token_name):
        """
        Check that ``token_name`` is a known token.
        
        :param token_name: The token's name.
        :type token_name: basestring
        :raises GrammarError: If the ``token_name`` is unknown.
        
        """
        if token_name not in self.default_tokens:
            raise GrammarError('Unknown token "%s"' % token_name)
    
    #{ Settings handling
    
    def get_setting(self, setting_name):
        """
        Return the value of setting identified by ``setting_name``.
        
        :param setting_name: The name of the setting to be retrieved.
        :type setting_name: basestring
        :return: The setting value.
        :raises GrammarError: If the ``setting_name`` is unknown.
        
        """
        self._check_setting_existence(setting_name)
        return self._custom_settings.get(setting_name,
                                         self.default_settings[setting_name])
    
    def set_setting(self, setting_name, setting):
        """
        Set the setting called ``setting_name`` to the custom value ``setting``.
        
        :param setting_name: The name of the setting to be customized.
        :type setting_name: basestring
        :param setting: The new value of the setting.
        :type setting: basestring
        :raises GrammarError: If the ``setting_name`` is unknown or ``setting``
            is an invalid value for ``setting_name``.
        
        Settings whose expected value is a Python boolean are not validated.
        
        """
        self._check_setting_existence(setting_name)
        self._custom_settings[setting_name] = setting
    
    def _check_setting_existence(self, setting_name):
        """
        Check that ``setting_name`` is a known setting.
        
        :param setting_name: The setting's name.
        :type setting_name: basestring
        :raises GrammarError: If the ``setting_name`` is unknown.
        
        """
        if setting_name not in self.default_settings:
            raise GrammarError('Unknown setting "%s"' % setting_name)
    
    # Custom generator handling
    
    def get_custom_generator(self, generator_name):
        """
        Return the generator identified by ``generator_name``.
        
        :param generator_name: The name of the generator to be retrieved.
        :type generator_name: basestring
        :return: The generator value or ``None`` if it's not been set.
        :raises GrammarError: If the ``generator_name`` is unknown.
        
        """
        self._check_generator_existence(generator_name)
        return self._custom_generators.get(generator_name)
    
    def set_custom_generator(self, generator_name, generator):
        """
        Set the generator called ``generator_name`` to the custom callable
        ``generator``.
        
        :param generator_name: The name of the generator to be overridden.
        :type generator_name: basestring
        :param generator: The custom generator (a Python callable).
        :raises GrammarError: If the ``generator_name`` is unknown.
        
        """
        self._check_generator_existence(generator_name)
        self._custom_generators[generator_name] = generator
    
    def _check_generator_existence(self, generator_name):
        """
        Check that ``generator_name`` is a known generator.
        
        :param generator_name: The generator's name.
        :type generator_name: basestring
        :raises GrammarError: If the ``generator_name`` is unknown.
        
        """
        if generator_name not in self.known_generators:
            raise GrammarError('Unknown generator "%s"' % generator_name)
    
    #}


class Parser(object):
    """
    Base class for parsers.
    
    """
    
    parse_tree_class = None
    
    def __init__(self, grammar, namespace):
        self._parser = None
        self._grammar = grammar
        self._namespace = namespace
    
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
        relationals = eq | ne | lt | gt | le | ge
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
        and_ = CaselessLiteral(self._grammar.get_token("and"))
        in_or = CaselessLiteral(self._grammar.get_token("or"))
        ex_or = CaselessLiteral(self._grammar.get_token("xor"))
        or_ = in_or | ex_or
        
        operand = self.define_operand()
        
        operation = operatorPrecedence(
            operand,
            [
                (relationals, 2, opAssoc.LEFT, self.make_relational),
                #(not_, 1, opAssoc.RIGHT),
                (and_, 2, opAssoc.LEFT),
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
        variable = identifier.setName("variable")
        variable.addParseAction(self.make_variable)
        
        # Defining the functions:
        function_name = identifier.setName("function_name")
        args_start = Suppress(self._grammar.get_token("arguments_start"))
        args_end = Suppress(self._grammar.get_token("arguments_end"))
        args_sep = self._grammar.get_token("arguments_separator")
        arguments = Optional(delimitedList(operand, delim=args_sep))
        function = Group(function_name + args_start + arguments + args_end)
        function.setParseAction(self.make_function)
        
        operand << (variable | self.define_number() | \
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
        # Defining the individual indentifiers:
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
        
        identifier = namespace + identifier0
        identifier.setName("identifier")
        
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
    
    #}


class EvaluableParser(Parser):
    """
    Evaluable parser.
    
    """
    
    parse_tree_class = EvaluableParseTree
    
    def make_variable(self, tokens):
        """Make a Variable using the token passed."""
        var = self._namespace.get_object(tokens[0][0], tokens[0][1])
        # TODO: Check that it's a variable!!!
        return var
    
    def make_function(self, tokens):
        """Make a Function using the token passed."""
        return Function(tokens[0])


class ConvertibleParser(Parser):
    """
    Convertible parser.
    
    """
    
    parse_tree_class = ConvertibleParseTree
    
    def make_variable(self, tokens):
        """Make a Variable placeholder using the token passed."""
        return VariablePlaceholder(tokens[0])
    
    def make_function(self, tokens):
        """Make a Function placeholder using the token passed."""
        return FunctionPlaceholder(tokens[0])

