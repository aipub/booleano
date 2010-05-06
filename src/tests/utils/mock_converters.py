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
Mock converters.

"""
from booleano.nodes.converters import BaseConverter
from booleano.nodes.operations import (Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, BelongsTo, IsSubset)
from booleano.nodes.constants import (String, Number, Set, PlaceholderVariable,
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


