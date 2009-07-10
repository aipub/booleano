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
Parser of boolean expressions.

"""

__all__ = ("ParseManager", "EvaluableParser", "ConvertibleParser", "Grammar",
           "Bind", "SymbolTable")


# TODO: Get a better name for this.
class ParseManager(object):
    
    def __init__(self,
                 symbol_table,
                 generic_grammar,
                 tree_type="evaluable",
                 cache_limit=-1,
                 **localized_grammars):
        self.cache_limit = cache_limit
        prepared_parsers = {}
        for (locale, grammar) in grammar:
            parser.set_namespace(symbol_table.get_namespace(locale))
            prepared_parsers[locale] = parser
    
    def get_parser(self, locale):
        raise NotImplementedError()
    
    def parse_evaluable(self, expression, locale, context):
        raise NotImplementedError
    
    def parse_convertible(self, expression, locale):
        raise NotImplementedError


# Importing the objects to be available from this namespace:
from booleano.parser.scope import Bind, SymbolTable
from booleano.parser.parsers import EvaluableParser, ConvertibleParser
from booleano.parser.grammar import Grammar
