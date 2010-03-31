# -*- coding: utf-8 -*-
#
# Copyright (c) 2009-2010 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://booleano.efous.org/>.
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
Mock converters.

"""
from booleano.nodes.converters import BaseConverter
from booleano.nodes.operations import (Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset)
from booleano.nodes.operands import (String, Number, Set, PlaceholderVariable,
                                     PlaceholderFunction)


class AntiConverter(BaseConverter):
    """
    A parse tree converter that returns the original parse tree, ignoring the
    namespaces in the constants.
    
    This is the simplest way to check the converter.
    
    """
    
    def convert_not(self, operand):
        return Not(operand)
    
    def convert_and(self, master_operand, slave_operand):
        return And(master_operand, slave_operand)
    
    def convert_or(self, master_operand, slave_operand):
        return Or(master_operand, slave_operand)
    
    def convert_xor(self, master_operand, slave_operand):
        return Xor(master_operand, slave_operand)
    
    def convert_equal(self, master_operand, slave_operand):
        return Equal(master_operand, slave_operand)
    
    def convert_not_equal(self, master_operand, slave_operand):
        return NotEqual(master_operand, slave_operand)
    
    def convert_less_than(self, master_operand, slave_operand):
        return LessThan(master_operand, slave_operand)
    
    def convert_greater_than(self, master_operand, slave_operand):
        return GreaterThan(master_operand, slave_operand)
    
    def convert_less_equal(self, master_operand, slave_operand):
        return LessEqual(master_operand, slave_operand)
    
    def convert_greater_equal(self, master_operand, slave_operand):
        return GreaterEqual(master_operand, slave_operand)
    
    def convert_belongs_to(self, master_operand, slave_operand):
        return BelongsTo(slave_operand, master_operand,)
    
    def convert_is_subset(self, master_operand, slave_operand):
        return IsSubset(slave_operand, master_operand)
    
    def convert_string(self, text):
        return String(text)
    
    def convert_number(self, number):
        return Number(number)
    
    def convert_set(self, *elements):
        return Set(*elements)
    
    def convert_variable(self, name, namespace_parts):
        return PlaceholderVariable(name, namespace_parts)
    
    def convert_function(self, name, namespace_parts, *arguments):
        return PlaceholderFunction(name, namespace_parts, *arguments)


class StringConverter(BaseConverter):
    """
    Parse tree converter that turns the tree back into a string, based on a
    given grammar.
    
    """
    
    def __init__(self, grammar):
        """
        Set up the converter.
        
        :param grammar: The grammar to be used.
        :type grammar: Grammar
        
        """
        self.grammar = grammar
    
    def convert_not(self, operand):
        return u"%s %s" % (self.grammar.get_token("not"), operand)
    
    def __make_binary_infix__(self,
                              operator_token,
                              master_operand,
                              slave_operand):
        """Make a binary infix expression."""
        token = self.grammar.get_token(operator_token)
        group_start = self.grammar.get_token("group_start")
        group_end = self.grammar.get_token("group_end")
        all_tokens = (group_start, master_operand, token, slave_operand,
                      group_end)
        expression = u" ".join(all_tokens)
        return expression
    
    def convert_and(self, master_operand, slave_operand):
        return self.__make_binary_infix__("and", master_operand, slave_operand)
    
    def convert_or(self, master_operand, slave_operand):
        return self.__make_binary_infix__("or", master_operand, slave_operand)
    
    def convert_xor(self, master_operand, slave_operand):
        return self.__make_binary_infix__("xor", master_operand, slave_operand)
    
    def convert_equal(self, master_operand, slave_operand):
        return self.__make_binary_infix__("eq", master_operand, slave_operand)
    
    def convert_not_equal(self, master_operand, slave_operand):
        return self.__make_binary_infix__("ne", master_operand, slave_operand)
    
    def convert_less_than(self, master_operand, slave_operand):
        return self.__make_binary_infix__("lt", master_operand, slave_operand)
    
    def convert_greater_than(self, master_operand, slave_operand):
        return self.__make_binary_infix__("gt", master_operand, slave_operand)
    
    def convert_less_equal(self, master_operand, slave_operand):
        return self.__make_binary_infix__("le", master_operand, slave_operand)
    
    def convert_greater_equal(self, master_operand, slave_operand):
        return self.__make_binary_infix__("ge", master_operand, slave_operand)
    
    def convert_belongs_to(self, master_operand, slave_operand):
        return self.__make_binary_infix__("belongs_to", slave_operand,
                                          master_operand)
    
    def convert_is_subset(self, master_operand, slave_operand):
        return self.__make_binary_infix__("is_subset", slave_operand,
                                          master_operand)
    
    def convert_string(self, text):
        return u'"%s"' % text
    
    def convert_number(self, number):
        # TODO: Number properties such as decimal separator must be taken into
        # account.
        return unicode(number)
    
    def convert_set(self, *elements):
        element_sep = self.grammar.get_token("element_separator") + " "
        elements = element_sep.join(elements)
        set_start = self.grammar.get_token("set_start")
        set_end = self.grammar.get_token("set_end")
        return set_start + elements + set_end
    
    def convert_variable(self, name, namespace_parts):
        return self.__build_identifier__(name, namespace_parts)
    
    def convert_function(self, name, namespace_parts, *arguments):
        identifier = self.__build_identifier__(name, namespace_parts)
        arg_start = self.grammar.get_token("arguments_start")
        arg_end = self.grammar.get_token("arguments_end")
        arg_sep = self.grammar.get_token("arguments_separator") + " "
        arguments = arg_sep.join(arguments)
        return identifier + arg_start + arguments + arg_end
    
    def __build_identifier__(self, name, namespace_parts):
        if not namespace_parts:
            return name
        ns_sep = self.grammar.get_token("namespace_separator")
        namespace = ns_sep.join(namespace_parts)
        identifier = namespace + ns_sep + name
        return identifier


