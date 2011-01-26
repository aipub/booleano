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
Test suite for the generic Pyparsing helpers defined in Booleano.

"""

from nose.tools import assert_raises
from pyparsing import (Literal, NoMatch)

from booleano.parser._helpers import make_operations, _append_operation


OPERAND_A = Literal("operand")
OPERAND_B = Literal("operand1") | Literal("operand2")
OPERATOR_A = Literal("operatorA")
OPERATOR_B = Literal("operatorB")


class TestOperationMaker(object):
    """
    Tests for make_operations().
    
    """
    
    def test_wrong_arity(self):
        pass


class TestOperationAddition(object):
    """
    Tests for _append_operation().
    
    """
    # TODO:
    pass

