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
Adaptive grammar definition and handling.

"""

from booleano.exc import GrammarError


__all__ = ("Grammar", )


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
    """The default tokens."""
    
    default_settings = {
        'superset_right_in_is_subset': True,
        'set_right_in_contains': True,
        'optional_positive_sign': True,
    }
    """The default settings for the grammar."""
    
    known_generators = set([
        "operation",
        "string",
        "number",
    ])
    """The known/valid generators."""
    
    def __init__(self, settings=None, generators=None, **tokens):
        """
        
        :param settings: The grammar settings to be overridden, if any.
        :type settings: dict
        :param generators: The custom Pyparsing generators for some of the
            elements in the grammar, if any.
        :type generators: dict
        :raises booleano.exc.GrammarError: If at least one of the ``settings``,
            ``generators`` or ``tokens`` are not valid.
        
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
        :raises booleano.exc.GrammarError: If the ``token_name`` is unknown.
        
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
        :raises booleano.exc.GrammarError: If the ``token_name`` is unknown.
        
        """
        self._check_token_existence(token_name)
        self._custom_tokens[token_name] = token
    
    def _check_token_existence(self, token_name):
        """
        Check that ``token_name`` is a known token.
        
        :param token_name: The token's name.
        :type token_name: basestring
        :raises booleano.exc.GrammarError: If the ``token_name`` is unknown.
        
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
        :raises booleano.exc.GrammarError: If the ``setting_name`` is unknown.
        
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
        :raises booleano.exc.GrammarError: If the ``setting_name`` is
            unknown or ``setting`` is an invalid value for ``setting_name``.
        
        Settings whose expected value is a Python boolean are not validated.
        
        """
        self._check_setting_existence(setting_name)
        self._custom_settings[setting_name] = setting
    
    def _check_setting_existence(self, setting_name):
        """
        Check that ``setting_name`` is a known setting.
        
        :param setting_name: The setting's name.
        :type setting_name: basestring
        :raises booleano.exc.GrammarError: If the ``setting_name`` is unknown.
        
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
        :raises booleano.exc.GrammarError: If the ``generator_name`` is unknown.
        
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
        :raises booleano.exc.GrammarError: If the ``generator_name`` is unknown.
        
        """
        self._check_generator_existence(generator_name)
        self._custom_generators[generator_name] = generator
    
    def _check_generator_existence(self, generator_name):
        """
        Check that ``generator_name`` is a known generator.
        
        :param generator_name: The generator's name.
        :type generator_name: basestring
        :raises booleano.exc.GrammarError: If the ``generator_name`` is unknown.
        
        """
        if generator_name not in self.known_generators:
            raise GrammarError('Unknown generator "%s"' % generator_name)
    
    #}
