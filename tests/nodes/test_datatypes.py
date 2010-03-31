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
Test suite for the datatypes.

We basically want to test abstract functionality.

"""
from nose.tools import ok_, assert_false, assert_raises

from booleano.nodes.datatypes import (Datatype, BooleanType, NumberType,
                                      StringType, SetType)


def test_inheritance():
    """All the datatypes are descendant of Datatype."""
    ok_(issubclass(BooleanType, Datatype))
    ok_(issubclass(NumberType, Datatype))
    ok_(issubclass(StringType, Datatype))
    ok_(issubclass(SetType, Datatype))


def test_instantiation():
    """Datatypes cannot be instantiated directly -- they're all abstract."""
    assert_raises(TypeError, BooleanType)
    assert_raises(TypeError, NumberType)
    assert_raises(TypeError, StringType)
    assert_raises(TypeError, SetType)


def test_boolean_callable():
    """Booleans can be called directly to get the logical value."""
    positive_bool = MockBoolean(True)
    negative_bool = MockBoolean(False)
    ok_(positive_bool(None))
    assert_false(negative_bool(None))


#{ Test utilities


class MockBoolean(BooleanType):
    
    def __init__(self, result):
        self.result = result
    
    def get_as_boolean(self, context):
        return self.result


#}
