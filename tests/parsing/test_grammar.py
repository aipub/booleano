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
Test suite for the grammar configurations.

"""

from nose.tools import eq_, ok_, assert_raises

from booleano.parser.generic import Grammar
from booleano.exc import GrammarError


class TestDefaultGrammar(object):
    """Tests for the grammar with the default properties, at least initially."""
    
    def setUp(self):
        self.grammar = Grammar()
    
    #{ Token handling stuff
    
    def test_default_tokens(self):
        """All the tokens must have an initial value."""
        # Logical connectives:
        eq_(self.grammar.get_token("not"), "~")
        eq_(self.grammar.get_token("and"), "&")
        eq_(self.grammar.get_token("or"), "|")
        eq_(self.grammar.get_token("xor"), "^")
        # Relational operators
        eq_(self.grammar.get_token("eq"), "==")
        eq_(self.grammar.get_token("ne"), "!=")
        eq_(self.grammar.get_token("lt"), "<")
        eq_(self.grammar.get_token("gt"), ">")
        eq_(self.grammar.get_token("le"), "<=")
        eq_(self.grammar.get_token("ge"), ">=")
        # Set operators
        eq_(self.grammar.get_token("in"), u"∈")
        eq_(self.grammar.get_token("contained"), u"⊂")
        eq_(self.grammar.get_token("set_start"), "{")
        eq_(self.grammar.get_token("set_end"), "}")
        eq_(self.grammar.get_token("element_separator"), ",")
        # Grouping marks
        eq_(self.grammar.get_token("string_start"), '"')
        eq_(self.grammar.get_token("string_end"), '"')
        eq_(self.grammar.get_token("group_start"), "(")
        eq_(self.grammar.get_token("group_end"), ")")
        # Function call stuff
        eq_(self.grammar.get_token("arguments_start"), "(")
        eq_(self.grammar.get_token("arguments_end"), ")")
        eq_(self.grammar.get_token("arguments_separator"), ",")
        # Numeric stuff
        eq_(self.grammar.get_token("positive_sign"), "+")
        eq_(self.grammar.get_token("negative_sign"), "-")
        eq_(self.grammar.get_token("decimal_separator"), ".")
        eq_(self.grammar.get_token("thousands_separator"), ",")
        # Miscellaneous
        eq_(self.grammar.get_token("identifier_spacing"), "_")
        eq_(self.grammar.get_token("namespace_separator"), ":")
    
    def test_setting_existing_token(self):
        self.grammar.set_token("negative_sign", "!")
        eq_(self.grammar.get_token("negative_sign"), "!")
    
    def test_requesting_non_existing_token(self):
        assert_raises(GrammarError, self.grammar.get_token, "non_existing")
    
    def test_setting_non_existing_token(self):
        assert_raises(GrammarError, self.grammar.set_token, "non_existing", "-")
    
    #{ Setting handling stuff
    
    def test_default_settings(self):
        eq_(self.grammar.get_setting("superset_right_in_is_subset"), True)
        eq_(self.grammar.get_setting("set_right_in_contains"), True)
        eq_(self.grammar.get_setting("optional_positive_sign"), True)
    
    def test_setting_existing_setting(self):
        self.grammar.set_setting("set_right_in_contains", False)
        eq_(self.grammar.get_setting("set_right_in_contains"), False)
    
    def test_requesting_non_existing_setting(self):
        assert_raises(GrammarError, self.grammar.get_setting, "non_existing")
    
    def test_setting_non_existing_setting(self):
        assert_raises(GrammarError, self.grammar.set_setting, "non_existing",
                      None)
    
    #{ Custom generator handling stuff
    
    def test_no_custom_generators_by_default(self):
        """There must not be custom generators by default."""
        eq_(self.grammar.get_custom_generator("operation"), None)
        eq_(self.grammar.get_custom_generator("string"), None)
        eq_(self.grammar.get_custom_generator("number"), None)
    
    def test_setting_existing_generator(self):
        mock_generator = lambda: None
        self.grammar.set_custom_generator("number", mock_generator)
        eq_(self.grammar.get_custom_generator("number"), mock_generator)
    
    def test_requesting_non_existing_generator(self):
        assert_raises(GrammarError, self.grammar.get_custom_generator,
                      "non_existing")
    
    def test_setting_non_existing_generator(self):
        mock_generator = lambda: None
        assert_raises(GrammarError, self.grammar.set_custom_generator,
                      "non_existing", mock_generator)
    
    #}
