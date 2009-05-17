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
Mock parse tree elements to test the actual parse trees.

The classes defined here are all in upper-case on purpose, which is anti-PEP 8,
in order to distinguish them from the actual operand and operation classes
(which are all PEP 8 compliant).

"""
from nose.tools import eq_, ok_, raises

from booleano.operations.operators import (FunctionOperator, TruthOperator,
        NotOperator, AndOperator, OrOperator, XorOperator, EqualOperator,
        LessThanOperator, GreaterThanOperator, LessEqualOperator, 
        GreaterEqualOperator, ContainsOperator, SubsetOperator)
from booleano.operations.operands import (String, Number, Set, Variable)

__all__ = ["STRING", "NUMBER", "VARIABLE", "SET"]


#{ Mock operands


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
            u'"%s" must be an instance of %s' % (repr(value),
                                                 self.operand_class))
        original_value = self.value
        actual_value = self.get_actual_value(value)
        eq_(original_value, actual_value,
            u'%s must equal "%s"' % (self, actual_value))
    
    def get_actual_value(self, value):
        raise NotImplementedError


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
    
    def __init__(self, *elements):
        """Store ``elements`` as a single value (a tuple)."""
        super(SET, self).__init__(elements)
    
    def equals(self, value):
        """
        Check that the elements in set ``value`` are the same elements
        contained in this mock set.
        
        """
        unmatched_values = list(self.value)
        eq_(len(unmatched_values), len(value.constant_value),
            u'Sets "%s" and "%s" do not have the same cardinality' %
            (unmatched_values, value))
        
        # Checking that each element is represented by a mock operand:
        for element in value.constant_value:
            for key in range(len(unmatched_values)):
                try:
                    unmatched_values[key].equals(element)
                except AssertionError:
                    continue
                del unmatched_values[key]
                break
        
        eq_(0, len(unmatched_values),
            u'No match for the following elements: %s' % unmatched_values)
    
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


#{ Mock operations


class MockOperation(object):
    """
    Represent an operation.
    
    """
    
    def __init__(self, *operands):
        self.operands = operands
    
    def equals(self, operation):
        """
        Check if ``operation`` equals this operation.
        
        """
        ok_(isinstance(operation, self.operation_class),
            u'Operator "%s" must be an instance of %s' % (repr(operator),
                                                          self.operation_class))
        operands = self.get_operands(operation)
        
        eq_(len(self.operands), len(operands),
            'Operation "%s" does not have the same operands as operation "%s"' \
            % (self, operation))
        
        for pos in range(len(operands)):
            self.operands[pos].equals(operands[pos])
    
    def get_operands(self, operation):
        raise NotImplementedError


#}
