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
Mock operands and operators to represent the data structures in a parse tree.

The classes defined here are all capitalized and that's anti-PEP-0008, but it
helps to distinguish them clearly from the actual operands and operators.

"""

from nose.tools import eq_, ok_

from booleano.operations.operators import (FunctionOperator, TruthOperator,
        NotOperator, AndOperator, OrOperator, XorOperator, EqualityOperator,
        LessThanOperator, GreaterThanOperator, LessEqualOperator, 
        GreaterEqualOperator, ContainsOperator, SubsetOperator)
from booleano.operations.operands import (String, Number, Set, Variable)


class MockOperand(object):
    """
    Represent an operand.
    
    """
    
    def __init__(self, value):
        """
        Store the ``value`` represented by the operand.
        
        """
        self.value = value
    
    def equals(self, value):
        """Check if ``value`` equals this operand."""
        ok_(isinstance(value, self.operand_class),
            u'"%s" must be an instance of %s' % (value, self.operand_class))
        original_value = self.value
        actual_value = self.get_actual_value(value)
        eq_(original_value, actual_value,
            u'%s must equal "%s"' % (self, actual_value))
    
    def get_actual_value(self, value):
        raise NotImplementedError


class MockOperation(object):
    """
    Represent an operation.
    
    """
    def __init__(self, operator, *operands):
        self.operator = operator
        self.operands = operands


#{ Operands


class _MockConstant(MockOperand):
    """Base class for mock constants."""
    
    def get_actual_value(self, value):
        """Return the value represented by the ``value`` constant."""
        return value.constant_value


class STRING(_MockConstant):
    """Mock string constant."""
    
    operand_class = String
    
    def __unicode__(self):
        return 'Constant string "%s"' % self.value


class NUMBER(_MockConstant):
    """Mock number constant."""
    
    operand_class = Number
    
    def __unicode__(self):
        return 'Constant number %s' % self.value


class SET(_MockConstant):
    """Mock set constant."""
    
    operand_class = Set
    
    def __unicode__(self):
        return 'Constant set %s' % self.value


class VARIABLE(MockOperand):
    """Mock variable."""
    operand_class = Variable
    
    def __init__(self, value, language=None):
        self.language = language
        super(VARIABLE, self).__init__(value)
    
    def get_actual_value(self, value):
        if not self.language:
            return value.global_name
        return value.names[self.language]
    
    def __unicode__(self):
        return 'Variable "%s"' % self.value


#}
