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
Tests for unbounded operands.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises, raises

from booleano.exc import (InvalidOperationError, BadOperandError, BadCallError,
                          BadFunctionError)
from booleano.nodes.datatypes import NumberType, SetType, StringType
from booleano.nodes.operands import Constant, String, Number, Set#, Variable,
#    Function)
#
#from tests.utils.mock_operands import (TrafficLightVar, PermissiveFunction,
#                                       TrafficViolationFunc, BoolVar)


#{ Variables


class TestVariable(object):
    """Tests for variable operands."""
    
    def test_node_type(self):
        """Variables are leaf nodes."""
        var = BoolVar()
        ok_(var.is_leaf())
        assert_false(var.is_branch())
    
    def test_checking_supported_operations(self):
        class GreetingVariable(Variable):
            operations = set(["equality"])
            
            def to_python(self, context):
                pass
            
            def equals(self, value, context):
                pass
    
    @raises(BadOperandError)
    def test_checking_unsupported_operations(self):
        class GreetingVariable(Variable):
            operations = set(["equality"])
            
            def to_python(self, context):
                pass
    
    def test_checking_logical_support(self):
        class GreetingVariable(Variable):
            operations = set(["equality"])
            def to_python(self, context):
                pass
            def equals(self, value, context):
                pass
        
        var1 = BoolVar()
        var2 = GreetingVariable()
        # Checking logical support:
        var1.check_logical_support()
        assert_raises(InvalidOperationError, var2.check_logical_support)
    
    def test_equivalence(self):
        """Two variables are equivalent if they share the same class."""
        var1 = TrafficLightVar()
        var2 = TrafficLightVar()
        var3 = BoolVar()
        
        var1.check_equivalence(var2)
        var2.check_equivalence(var1)
        
        assert_raises(AssertionError, var1.check_equivalence, var3)
        assert_raises(AssertionError, var2.check_equivalence, var3)
        assert_raises(AssertionError, var3.check_equivalence, var1)
        assert_raises(AssertionError, var3.check_equivalence, var1)
        
        ok_(var1 == var2)
        ok_(var2 == var1)
        ok_(var1 != var3)
        ok_(var2 != var3)
        ok_(var3 != var1)
        ok_(var3 != var2)
    
    def test_string_representation(self):
        var = TrafficLightVar()
        as_unicode = unicode(var)
        eq_("Anonymous variable [TrafficLightVar]", as_unicode)
        eq_(str(var), as_unicode)
    
    def test_representation(self):
        var = TrafficLightVar()
        eq_(repr(var), "<Anonymous variable [TrafficLightVar]>")


class TestFunction(object):
    """Tests for the base class of user-defined function operators."""
    
    def test_node_type(self):
        """Functions are branch nodes."""
        func = PermissiveFunction(String("arg0"))
        ok_(func.is_branch())
        assert_false(func.is_leaf())
    
    def test_checking_supported_operations(self):
        class GreetingFunction(Function):
            operations = set(["equality"])
            
            def to_python(self, context):
                pass
            
            def equals(self, value, context):
                pass
    
    @raises(BadOperandError)
    def test_checking_unsupported_operations(self):
        class GreetingFunction(Function):
            operations = set(["equality"])
            
            def to_python(self, context):
                pass
    
    def test_constructor_with_minimum_arguments(self):
        func = PermissiveFunction(String("this-is-arg0"))
        args = {
            'arg0': String("this-is-arg0"),
            'oarg0': Set(),
            'oarg1': Number(1),
        }
        eq_(func.arguments, args)
    
    def test_constructor_with_one_optional_argument(self):
        func = PermissiveFunction(String("this-is-arg0"),
                                  String("this-is-oarg0"))
        args = {
            'arg0': String("this-is-arg0"),
            'oarg0': String("this-is-oarg0"),
            'oarg1': Number(1),
        }
        eq_(func.arguments, args)
    
    def test_constructor_with_all_arguments(self):
        func = PermissiveFunction(
            String("this-is-arg0"),
            String("this-is-oarg0"),
            String("this-is-oarg1"),
        )
        args = {
            'arg0': String("this-is-arg0"),
            'oarg0': String("this-is-oarg0"),
            'oarg1': String("this-is-oarg1"),
        }
        eq_(func.arguments, args)
    
    @raises(BadCallError)
    def test_constructor_with_few_arguments(self):
        PermissiveFunction()
    
    @raises(BadCallError)
    def test_constructor_with_many_arguments(self):
        PermissiveFunction(
            Number(0),
            Number(1),
            Number(2),
            Number(3),
            Number(4),
            Number(5),
            Number(6),
            Number(7),
            Number(8),
            Number(9),
        )
    
    def test_constructor_accepts_operands(self):
        """Only operands are valid function arguments."""
        PermissiveFunction(Number(0), Number(1))
        assert_raises(BadCallError, PermissiveFunction, 0, 1)
    
    def test_no_argument_validation_by_default(self):
        """
        Arguments must be explicitly validated by the function.
        
        This is, their .check_arguments() method must be overriden.
        
        """
        class MockFunction(Function):
            bypass_operation_check = True
        assert_raises(NotImplementedError, MockFunction)
    
    def test_arity(self):
        """
        The arity and all the arguments for a function must be calculated
        right after it's been defined.
        
        """
        # Nullary function:
        class NullaryFunction(Function):
            bypass_operation_check = True
        eq_(NullaryFunction.arity, 0)
        eq_(NullaryFunction.all_args, ())
        
        # Unary function:
        class UnaryFunction(Function):
            bypass_operation_check = True
            required_arguments = ("arg1", )
        eq_(UnaryFunction.arity, 1)
        eq_(UnaryFunction.all_args, ("arg1", ))
        
        # Unary function, with its argument optional:
        class OptionalUnaryFunction(Function):
            bypass_operation_check = True
            optional_arguments = {'oarg1': Set()}
        eq_(OptionalUnaryFunction.arity, 1)
        eq_(OptionalUnaryFunction.all_args, ("oarg1", ))
        
        # Binary function:
        class BinaryFunction(Function):
            bypass_operation_check = True
            required_arguments = ("arg1", )
            optional_arguments = {'oarg1': Set()}
        eq_(BinaryFunction.arity, 2)
        eq_(BinaryFunction.all_args, ("arg1", "oarg1"))
    
    @raises(BadFunctionError)
    def test_duplicate_arguments(self):
        """An optional argument shouldn't share its name with a required one"""
        class FunctionWithDuplicateArguments(Function):
            required_arguments = ("arg1", )
            optional_arguments = {'arg1': None}
    
    @raises(BadFunctionError)
    def test_duplicate_required_arguments(self):
        """Two required arguments must not share the same name."""
        class FunctionWithDuplicateArguments(Function):
            required_arguments = ("arg1", "arg1")
    
    @raises(BadFunctionError)
    def test_non_operand_default_arguments(self):
        """Default values for the optional arguments must be operands."""
        class FunctionWithNonOperands(Function):
            bypass_operation_check = True
            optional_arguments = {'arg': 1}
    
    def test_checking_logical_support(self):
        class NoBoolFunction(Function):
            operations = set(["equality"])
            def equals(self, node): pass
            def to_python(self): pass
            def check_arguments(self): pass
        
        func1 = PermissiveFunction(String("foo"))
        func2 = NoBoolFunction()
        # Checking logical support:
        func1.check_logical_support()
        assert_raises(InvalidOperationError, func2.check_logical_support)
    
    def test_equivalence(self):
        """
        Two functions are equivalent not only if they share the same class,
        but also if their arguments are equivalent.
        
        """
        class FooFunction(Function):
            bypass_operation_check = True
            required_arguments = ("abc", )
            optional_arguments = {"xyz": String("123")}
            def check_arguments(self): pass
        
        func1 = FooFunction(String("whatever"))
        func2 = FooFunction(String("whatever"))
        func3 = TrafficViolationFunc(String("pedestrians"))
        func4 = PermissiveFunction(String("foo"))
        func5 = FooFunction(String("something"))
        
        func1.check_equivalence(func2)
        func2.check_equivalence(func1)
        
        assert_raises(AssertionError, func1.check_equivalence, func3)
        assert_raises(AssertionError, func1.check_equivalence, func4)
        assert_raises(AssertionError, func1.check_equivalence, func5)
        assert_raises(AssertionError, func2.check_equivalence, func3)
        assert_raises(AssertionError, func2.check_equivalence, func4)
        assert_raises(AssertionError, func2.check_equivalence, func5)
        assert_raises(AssertionError, func3.check_equivalence, func1)
        assert_raises(AssertionError, func3.check_equivalence, func2)
        assert_raises(AssertionError, func3.check_equivalence, func4)
        assert_raises(AssertionError, func3.check_equivalence, func5)
        assert_raises(AssertionError, func4.check_equivalence, func1)
        assert_raises(AssertionError, func4.check_equivalence, func2)
        assert_raises(AssertionError, func4.check_equivalence, func3)
        assert_raises(AssertionError, func4.check_equivalence, func5)
        assert_raises(AssertionError, func5.check_equivalence, func1)
        assert_raises(AssertionError, func5.check_equivalence, func2)
        assert_raises(AssertionError, func5.check_equivalence, func3)
        assert_raises(AssertionError, func5.check_equivalence, func4)
        
        ok_(func1 == func2)
        ok_(func2 == func1)
        ok_(func1 != func3)
        ok_(func1 != func4)
        ok_(func1 != func5)
        ok_(func2 != func3)
        ok_(func2 != func4)
        ok_(func2 != func5)
        ok_(func3 != func1)
        ok_(func3 != func2)
        ok_(func3 != func4)
        ok_(func3 != func5)
        ok_(func4 != func1)
        ok_(func4 != func2)
        ok_(func4 != func3)
        ok_(func4 != func5)
        ok_(func5 != func1)
        ok_(func5 != func2)
        ok_(func5 != func3)
        ok_(func5 != func4)
    
    def test_string_representation(self):
        func = PermissiveFunction(String("foo"), String(u"bár"))
        expected = (u'Anonymous function call [PermissiveFunction](arg0="foo", '
                    u'oarg0="bár", oarg1=1.0)')
        eq_(unicode(func), expected)
        eq_(str(func), expected.encode("utf-8"))
    
    def test_representation(self):
        func = PermissiveFunction(String("foo"), String(u"báz"))
        expected = '<Anonymous function call [PermissiveFunction] ' \
                   'arg0=<String "foo">, oarg0=<String "báz">, ' \
                   'oarg1=<Number 1.0>>'
        eq_(repr(func), expected)


#{ Constants


class TestConstant(object):
    """Tests for the base :class:`Constant`."""
    
    def test_equality(self):
        """
        Two constants are equivalents if they represent the same Python constant
        value.
        
        """
        shared_value = object()
        constant1 = MockConstant(shared_value)
        constant2 = MockConstant(object())
        constant3 = MockConstant(shared_value)
        
        ok_(constant1 == constant1)
        assert_false(constant1 == constant2)
        ok_(constant1 == constant3)
        assert_false(constant2 == constant1)
        ok_(constant2 == constant2)
        assert_false(constant2 == constant3)
        ok_(constant3 == constant1)
        assert_false(constant3 == constant2)
        ok_(constant3 == constant3)


class TestString(object):
    """
    Tests for :class:`String` contants.
    
    """
    
    def test_node_type(self):
        """Strings are leaf nodes and implement the String datatype."""
        string = String("greeting")
        ok_(string.is_leaf)
        ok_(isinstance(string, StringType))
    
    def test_python_strings(self):
        """Constant strings represent Python :class:`unicode` objects."""
        ascii_text = String("tomorrow!")
        unicode_text = String(u"¡mañana!")
        
        py_ascii_text = ascii_text.get_as_string(None)
        py_unicode_text = unicode_text.get_as_string(None)
        
        ok_(isinstance(py_ascii_text, unicode))
        ok_(isinstance(py_unicode_text, unicode))
        
        eq_(py_ascii_text, u"tomorrow!")
        eq_(py_unicode_text, u"¡mañana!")
    
    def test_equivalence(self):
        """
        Two constant strings are equivalent if they represent the same string.
        
        """
        text1 = String("hello world")
        text2 = String("hello earth")
        text3 = String("hello world")
        
        ok_(text1 == text1)
        assert_false(text1 == text2)
        ok_(text1 == text3)
        assert_false(text2 == text1)
        ok_(text2 == text2)
        assert_false(text2 == text3)
        ok_(text3 == text1)
        assert_false(text3 == text2)
        ok_(text3 == text3)
    
    def test_representation(self):
        # With Unicode:
        string = String(u"caña")
        eq_(repr(string), '<String "caña">')
        # With ASCII
        string = String("cana")
        eq_(repr(string), '<String "cana">')


class TestNumber(object):
    """
    Tests for :class:`Number` constants.
    
    """
    
    def test_node_type(self):
        """Numbers are leaf nodes and implement the Number datatype."""
        number = Number(4)
        ok_(number.is_leaf)
        ok_(isinstance(number, NumberType))
    
    def test_python_numbers(self):
        """Constant numbers represent Python :class:`float` objects."""
        integer_number = Number(4)
        float_number = Number(2.5)
        
        py_integer_number = integer_number.get_as_number(None)
        py_float_number = float_number.get_as_number(None)
        
        ok_(isinstance(py_integer_number, float))
        ok_(isinstance(py_float_number, float))
        eq_(py_integer_number, 4.0)
        eq_(py_float_number, 2.5)
    
    def test_equivalence(self):
        """
        Two constant numbers are equivalent if they represent the same number.
        
        """
        number1 = Number(22)
        number2 = Number(23)
        number3 = Number(22)
        
        ok_(number1 == number1)
        assert_false(number1 == number2)
        ok_(number1 == number3)
        assert_false(number2 == number1)
        ok_(number2 == number2)
        assert_false(number2 == number3)
        ok_(number3 == number1)
        assert_false(number3 == number2)
        ok_(number3 == number3)
    
    def test_representation(self):
        number = Number(4)
        eq_(repr(number), "<Number 4.0>")


class TestSet(object):
    """
    Tests for :class:`Set` constants.
    
    """
    
    def test_node_type(self):
        """Sets are branch nodes and implement the Set datatype."""
        set_ = Set(String("arg0"))
        assert_false(set_.is_leaf)
        ok_(isinstance(set_, SetType))
    
    def test_instantiation(self):
        """All the members of a set must be operands"""
        # Instantiation with operands:
        Set(Number(3), String("hola"))
        # Instantiation with a non-operand value:
        try:
            Set(Number(3), "hola")
            assert False, "InvalidOperationError exception not raised"
        except InvalidOperationError, exc:
            assert 'Item "hola" is not an operand' in unicode(exc)
    
    def test_equivalence(self):
        """
        Two constant sets A and B are equivalent if they have the same
        cardinality and each element in A is equivalent to one element in B.
        
        """
        set1 = Set(String("hi"), Set(Number(3), String("hello")))
        set2 = Set(String("hi"), Number(3), String("hello"))
        set3 = Set(Set(String("hello"), Number(3)), String("hi"))
        set4 = Set(String("hi"), String("hello"))
        
        ok_(set1 == set1)
        assert_false(set1 == set2)
        ok_(set1 == set3)
        assert_false(set1 == set4)
        assert_false(set2 == set1)
        ok_(set2 == set2)
        assert_false(set2 == set3)
        assert_false(set2 == set4)
        ok_(set3 == set1)
        assert_false(set3 == set2)
        ok_(set3 == set3)
        assert_false(set3 == set4)
        assert_false(set4 == set1)
        assert_false(set4 == set2)
        assert_false(set4 == set3)
        ok_(set4 == set4)
    
    def test_representation(self):
        set1 = Set(Number(3), Number(5))
        eq_(repr(set1), "<Set <Number 3.0>, <Number 5.0>>")
        # Now with an empty set:
        set2 = Set()
        eq_(repr(set2), "<Set>")
        # Now with Unicode stuff in it:
        set3 = Set(String(u"España"), String(u"carabobeño"))
        eq_(repr(set3), '<Set <String "España">, <String "carabobeño">>')


#{ Test utilities


class MockConstant(Constant):
    """
    Mock constant which only implements abstract members.
    
    """
    
    is_leaf = True
    
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._constant_value)


#}
