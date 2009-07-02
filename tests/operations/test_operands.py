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
Tests for unbounded operands.

"""

from nose.tools import eq_, ok_, assert_false, assert_raises, raises

from booleano.operations import (String, Number, Set, Variable, Function,
                                 VariablePlaceholder, FunctionPlaceholder)
from booleano.operations.operands import Operand
from booleano.exc import (InvalidOperationError, BadOperandError, BadCallError,
                          BadFunctionError)

from tests import (TrafficLightVar, PermissiveFunction, TrafficViolationFunc,
                   BoolVar)


class TestOperand(object):
    """
    Tests for the base class Operand.
    
    """
    
    def setUp(self):
        """Create an instance of Operand"""
        self.op = Operand()
    
    def test_type(self):
        """Operand nodes must be known as operands."""
        ok_(self.op.is_operand())
        assert_false(self.op.is_operator())
    
    def test_supported_operations(self):
        """Operands shouldn't support any operation by default"""
        eq_(0, len(self.op.operations))
    
    def test_required_helpers(self):
        """Operands shouldn't require any helper by default"""
        eq_(0, len(self.op.required_helpers))
    
    def test_operation_methods(self):
        """No operation should be supported by default"""
        assert_raises(NotImplementedError, self.op.to_python)
        assert_raises(NotImplementedError, self.op.get_logical_value)
        assert_raises(NotImplementedError, self.op.equals, None)
        assert_raises(NotImplementedError, self.op.greater_than, None)
        assert_raises(NotImplementedError, self.op.less_than, None)
        assert_raises(NotImplementedError, self.op.contains, None)
        assert_raises(NotImplementedError, self.op.is_subset, None)
    
    def test_no_unicode_by_default(self):
        """Operands must not have a default Unicode representation."""
        assert_raises(NotImplementedError, unicode, self.op)
    
    def test_no_repr_by_default(self):
        """Operands must not have a default representation."""
        assert_raises(NotImplementedError, repr, self.op)
    
    #{ Operations support
    
    def test_checking_valid_operations(self):
        """Valid operations should just work."""
        class EqualityOperand(Operand):
            operations = set(["equality"])
            def to_python(self, value, **helpers):
                pass
            def equals(self, value, **helpers):
                pass
        
        class InequalityOperand(Operand):
            operations = set(["inequality"])
            def to_python(self, value, **helpers):
                pass
            def less_than(self, value, **helpers):
                pass
            def greater_than(self, value, **helpers):
                pass
        
        class BooleanOperand(Operand):
            operations = set(["boolean"])
            def to_python(self, value, **helpers):
                pass
            def get_logical_value(self, value, **helpers):
                pass
        
        class MembershipOperand(Operand):
            operations = set(["membership"])
            def to_python(self, value, **helpers):
                pass
            def contains(self, value, **helpers):
                pass
            def is_subset(self, value, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_invalid_operations(self):
        """Invalid operations must be detected."""
        class SillyOperand(Operand):
            operations = set(["equality", "addition"])
    
    @raises(BadOperandError)
    def test_checking_no_operation(self):
        """Operands must support at least one type of operation."""
        class BadOperand(Operand):
            operations = set()
    
    @raises(BadOperandError)
    def test_checking_no_to_python(self):
        """Operands must define the .to_python() method."""
        class BadOperand(Operand):
            operations = set(["equality"])
            def equals(self, value, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_no_logic_value(self):
        """
        Operands supporting truth values must define the .get_logical_value()
        method.
        
        """
        class BadOperand(Operand):
            operations = set(["boolean"])
            def to_python(self, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_no_equals(self):
        """Operands supporting equality must define the .equals() method."""
        class BadOperand(Operand):
            operations = set(["equality"])
            def to_python(self, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_no_lessthan_nor_greaterthan(self):
        """
        Operands supporting inequality must define the .less_than() and
        .greater_than() methods.
        
        """
        class BadOperand(Operand):
            operations = set(["inequality"])
            def to_python(self, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_no_lessthan(self):
        """
        Operands supporting inequality must define the .less_than() method.
        
        """
        class BadOperand(Operand):
            operations = set(["inequality"])
            def to_python(self, **helpers):
                pass
            def greater_than(self, value, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_no_greaterthan(self):
        """
        Operands supporting inequality must define the .greater_than() method.
        
        """
        class BadOperand(Operand):
            operations = set(["inequality"])
            def to_python(self, **helpers):
                pass
            def less_than(self, value, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_no_contains_nor_issubset(self):
        """
        Operands supporting membership must define the .contains() and
        .is_subset() methods.
        
        """
        class BadOperand(Operand):
            operations = set(["membership"])
            def to_python(self, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_no_contains(self):
        """
        Operands supporting membership must define the .contains() method.
        
        """
        class BadOperand(Operand):
            operations = set(["membership"])
            def to_python(self, **helpers):
                pass
            def is_subset(self, value, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_no_issubset(self):
        """
        Operands supporting membership must define the .is_subset() method.
        
        """
        class BadOperand(Operand):
            operations = set(["membership"])
            def to_python(self, **helpers):
                pass
            def contains(self, value, **helpers):
                pass
    
    def test_bypassing_operation_check(self):
        """Operations shouldn't be checked if asked so explicitly."""
        class BadOperand(Operand):
            bypass_operation_check = True
    
    @raises(BadOperandError)
    def test_bypassing_operation_check_not_inherited(self):
        """The operation support check setting shouldn't be inherited."""
        class ForgivenOperand(Operand):
            bypass_operation_check = True
        class BadOperand(ForgivenOperand):
            pass
    
    #}


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
            
            default_names = {'fr': "bonjour"}
            
            def to_python(self, **helpers):
                pass
            
            def equals(self, value, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_unsupported_operations(self):
        class GreetingVariable(Variable):
            operations = set(["equality"])
            
            default_names = {'fr': "bonjour"}
            
            def to_python(self, **helpers):
                pass
    
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
            
            default_names = {'fr': "bonjour"}
            
            def to_python(self, **helpers):
                pass
            
            def equals(self, value, **helpers):
                pass
    
    @raises(BadOperandError)
    def test_checking_unsupported_operations(self):
        class GreetingFunction(Function):
            operations = set(["equality"])
            
            default_names = {'fr': "bonjour"}
            
            def to_python(self, **helpers):
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


class TestString(object):
    """
    Tests for :class:`String` contants.
    
    """
    
    def test_node_type(self):
        """Strings are leaf nodes."""
        string = String("greeting")
        ok_(string.is_leaf())
        assert_false(string.is_branch())
    
    def test_operations(self):
        """String constants must only support equality operations"""
        eq_(String.operations, set(["equality"]))
    
    def test_python_value(self):
        op = String("carabobo")
        eq_(op.to_python(), "carabobo")
    
    def test_equality(self):
        op = String("freedomware")
        ok_(op.equals("freedomware"))
        assert_false(op.equals(" freedomware "))
        assert_false(op.equals("microsoftware"))
    
    def test_number_support(self):
        """Strings given as a number must be converted first into a string"""
        # When the constant is defined as a number:
        op = String(10)
        ok_(op.equals("10"))
        # When the constant is defined as a string:
        op = String("10")
        ok_(op.equals(10))
        # When both are defined as numbers:
        op = String(10)
        ok_(op.equals(10))
    
    def test_equivalence(self):
        """
        Two constant strings are equivalent if they represent the same string.
        
        """
        text1 = String("hello world")
        text2 = String("hello earth")
        text3 = String("hello world")
        
        text1.check_equivalence(text3)
        text3.check_equivalence(text1)
        
        assert_raises(AssertionError, text1.check_equivalence, text2)
        assert_raises(AssertionError, text2.check_equivalence, text1)
        assert_raises(AssertionError, text2.check_equivalence, text3)
        assert_raises(AssertionError, text3.check_equivalence, text2)
        
        ok_(text1 == text3)
        ok_(text3 == text1)
        ok_(text1 != text2)
        ok_(text2 != text1)
        ok_(text2 != text3)
        ok_(text3 != text2)
    
    def test_string_representation(self):
        string = String(u"caña")
        eq_(unicode(string), u'"caña"')
        eq_(str(string), '"caña"')
    
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
        """Numbers are leaf nodes."""
        number = Number(4)
        ok_(number.is_leaf())
        assert_false(number.is_branch())
    
    def test_operations(self):
        """
        Numeric constants must only support equality and inequality operations.
        
        """
        eq_(Number.operations, set(["equality", "inequality"]))
    
    def test_python_value(self):
        op = Number(22)
        eq_(op.to_python(), 22.00)
    
    def test_equality(self):
        # With an integer constant:
        op = Number(10)
        ok_(op.equals(10))
        ok_(op.equals(10.00))
        assert_false(op.equals(9.99999))
        assert_false(op.equals(10.00001))
        # With a float constant:
        op = Number(10.00)
        ok_(op.equals(10))
        ok_(op.equals(10.00))
        assert_false(op.equals(9.99999))
        assert_false(op.equals(10.00001))
        # Checking an invalid comparison:
        assert_raises(InvalidOperationError, op.equals, "today")
    
    def test_greater_than(self):
        # With an integer constant:
        op = Number(10)
        ok_(op.greater_than(9))
        ok_(op.greater_than(9.99999))
        assert_false(op.greater_than(10.00001))
        # With a float constant:
        op = Number(10.00)
        ok_(op.greater_than(9))
        ok_(op.greater_than(9.99999))
        assert_false(op.greater_than(10.00001))
        # With everything but a number:
        assert_raises(InvalidOperationError, op.greater_than, "ten")
    
    def test_less_than(self):
        # With an integer constant:
        op = Number(10)
        ok_(op.less_than(11))
        ok_(op.less_than(10.00001))
        assert_false(op.less_than(9.99999))
        # With a float constant:
        op = Number(10.00)
        ok_(op.less_than(11))
        ok_(op.less_than(10.00001))
        assert_false(op.less_than(9.99999))
        # With everything but a number:
        assert_raises(InvalidOperationError, op.less_than, "ten")
    
    def test_string_support(self):
        """Numbers given as strings must be converted first"""
        # The constant as a string:
        op = Number("10")
        ok_(op.equals(10))
        ok_(op.equals(10.00))
        # The other operand as string:
        op = Number(10)
        ok_(op.equals("10"))
        ok_(op.equals("10.00"))
        ok_(op.less_than("11"))
        ok_(op.greater_than("9"))
        assert_false(op.less_than("9"))
        assert_false(op.greater_than("11"))
    
    def test_equivalence(self):
        """
        Two constant numbers are equivalent if they represent the same number.
        
        """
        number1 = Number(22)
        number2 = Number(23)
        number3 = Number(22)
        
        number1.check_equivalence(number3)
        number3.check_equivalence(number1)
        assert_raises(AssertionError, number1.check_equivalence, number2)
        assert_raises(AssertionError, number2.check_equivalence, number1)
        assert_raises(AssertionError, number2.check_equivalence, number3)
        assert_raises(AssertionError, number3.check_equivalence, number2)
        
        ok_(number1 == number3)
        ok_(number3 == number1)
        ok_(number1 != number2)
        ok_(number2 != number1)
        ok_(number2 != number3)
        ok_(number3 != number2)
    
    def test_string_representation(self):
        number = Number(4)
        eq_(unicode(number), "4.0")
        eq_(str(number), "4.0")
    
    def test_representation(self):
        number = Number(4)
        eq_(repr(number), "<Number 4.0>")


class TestSet(object):
    """
    Tests for :class:`Set` constants.
    
    """
    
    def test_node_type(self):
        """Sets are branch nodes."""
        set_ = Set(String("arg0"))
        ok_(set_.is_branch())
        assert_false(set_.is_leaf())
    
    def test_operations(self):
        """
        Constant sets must only support equality, inequality and membership
        operations.
        
        """
        eq_(Set.operations, set(["equality", "inequality", "membership"]))
    
    def test_python_value(self):
        op = Set(Number(10), Number(1), String("paola"))
        eq_(op.to_python(), set((10, 1, "paola")))
    
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
    
    def test_equality(self):
        op = Set(Number(3), String("hola"))
        set1 = set([3, "hola"])
        set2 = set([3])
        set3 = set([3, "hola", "something else"])
        set4 = set(["nothing to do"])
        # Comparing them...
        ok_(op.equals(set1), "The constant equals %s" % op.constant_value)
        assert_false(op.equals(set2))
        assert_false(op.equals(set3))
        assert_false(op.equals(set4))
    
    def test_less_than(self):
        op = Set(String("carla"), String("andreina"), String("liliana"))
        ok_(op.less_than(4))
        ok_(op.less_than("4"))
        assert_false(op.less_than(2))
        assert_false(op.less_than(1))
        assert_raises(InvalidOperationError, op.less_than, "some string")
        assert_raises(InvalidOperationError, op.less_than, 3.10)
    
    def test_greater_than(self):
        op = Set(String("carla"), String("andreina"), String("liliana"))
        ok_(op.greater_than(2))
        ok_(op.greater_than("2"))
        assert_false(op.greater_than(3))
        assert_false(op.greater_than(4))
        assert_raises(InvalidOperationError, op.greater_than, "some string")
        assert_raises(InvalidOperationError, op.greater_than, 2.60)
    
    def test_contains(self):
        op = Set(String("arepa"), Number(4))
        ok_(op.contains(4))
        ok_(op.contains(4.00))
        ok_(op.contains("arepa"))
        assert_false(op.contains("something else"))
    
    def test_subset(self):
        op = Set(String("carla"), String("andreina"), String("liliana"))
        ok_(op.is_subset(["carla"]))
        ok_(op.is_subset(["carla", "liliana"]))
        ok_(op.is_subset(["andreina", "carla"]))
        assert_false(op.is_subset(["gustavo", "carlos"]))
        assert_false(op.is_subset(["carla", "gustavo"]))
    
    def test_equivalence(self):
        """
        Two constant sets A and B are equivalent if each element in A is
        equivalent to one element in B.
        
        """
        set1 = Set(String("hi"), Set(Number(3), String("hello")))
        set2 = Set(String("hi"), Number(3), String("hello"))
        set3 = Set(Set(String("hello"), Number(3)), String("hi"))
        set4 = Set(String("hi"), String("hello"))
        
        set1.check_equivalence(set3)
        set3.check_equivalence(set1)
        assert_raises(AssertionError, set1.check_equivalence, set2)
        assert_raises(AssertionError, set1.check_equivalence, set4)
        assert_raises(AssertionError, set2.check_equivalence, set1)
        assert_raises(AssertionError, set2.check_equivalence, set3)
        assert_raises(AssertionError, set2.check_equivalence, set4)
        assert_raises(AssertionError, set3.check_equivalence, set2)
        assert_raises(AssertionError, set3.check_equivalence, set4)
        assert_raises(AssertionError, set4.check_equivalence, set1)
        assert_raises(AssertionError, set4.check_equivalence, set2)
        assert_raises(AssertionError, set4.check_equivalence, set3)
        
        ok_(set1 == set3)
        ok_(set3 == set1)
        ok_(set1 != set2)
        ok_(set1 != set4)
        ok_(set2 != set1)
        ok_(set2 != set3)
        ok_(set2 != set4)
        ok_(set3 != set2)
        ok_(set3 != set4)
        ok_(set4 != set1)
        ok_(set4 != set2)
        ok_(set4 != set3)
    
    def test_string_representation(self):
        set_ = Set(Number(3), Number(5))
        as_unicode = unicode(set_)
        eq_(as_unicode, "{3.0, 5.0}")
        eq_(as_unicode, str(set_))
    
    def test_representation(self):
        set_ = Set(Number(3), Number(5))
        eq_(repr(set_), "<Set <Number 3.0>, <Number 5.0>>")
        # Now with an empty set:
        set_ = Set()
        eq_(repr(set_), "<Set>")


#{ Placeholders


class TestVariablePlaceholder(object):
    """Tests for the VariablePlaceholder."""
    
    def test_node_type(self):
        """Variable placeholders are leaf nodes."""
        var = VariablePlaceholder("greeting", None)
        ok_(var.is_leaf())
        assert_false(var.is_branch())
    
    def test_constructor(self):
        """
        Variable placeholders should contain an attribute which represents the
        name of the variable in question.
        
        """
        var1 = VariablePlaceholder(u"PAÍS", None)
        var2 = VariablePlaceholder("country", None)
        
        eq_(var1.name, u"país")
        eq_(var2.name, "country")
    
    def test_no_namespace(self):
        """Variable placeholders shouldn't have a default namespace."""
        var = VariablePlaceholder("foo")
        eq_(len(var.namespace_parts), 0)
    
    def test_namespaces(self):
        """Variable placeholders should be aware of their namespace."""
        var = VariablePlaceholder("country", ["geo", "bar"])
        eq_(var.namespace_parts, ["geo", "bar"])
    
    def test_no_operations(self):
        """Variable placeholders don't support operations."""
        var = VariablePlaceholder("var", None)
        assert_raises(InvalidOperationError, var.to_python)
        assert_raises(InvalidOperationError, var.get_logical_value)
        assert_raises(InvalidOperationError, var.equals, None)
        assert_raises(InvalidOperationError, var.less_than, None)
        assert_raises(InvalidOperationError, var.greater_than, None)
        assert_raises(InvalidOperationError, var.contains, None)
        assert_raises(InvalidOperationError, var.is_subset, None)
    
    def test_equivalence(self):
        """
        Two variable placeholders are equivalent if they have the same name
        and share the same namespace.
        
        """
        var1 = VariablePlaceholder("foo", None)
        var2 = VariablePlaceholder("bar", None)
        var3 = VariablePlaceholder("Foo", None)
        var4 = VariablePlaceholder("foo", ["some", "namespace"])
        var5 = VariablePlaceholder("bar", ["some", "namespace"])
        var6 = VariablePlaceholder("foo", ["some", "namespace"])
        
        var1.check_equivalence(var3)
        var3.check_equivalence(var1)
        var4.check_equivalence(var6)
        var6.check_equivalence(var4)
        
        assert_raises(AssertionError, var1.check_equivalence, var2)
        assert_raises(AssertionError, var1.check_equivalence, var4)
        assert_raises(AssertionError, var1.check_equivalence, var5)
        assert_raises(AssertionError, var1.check_equivalence, var6)
        assert_raises(AssertionError, var2.check_equivalence, var1)
        assert_raises(AssertionError, var2.check_equivalence, var3)
        assert_raises(AssertionError, var2.check_equivalence, var4)
        assert_raises(AssertionError, var2.check_equivalence, var5)
        assert_raises(AssertionError, var2.check_equivalence, var6)
        assert_raises(AssertionError, var3.check_equivalence, var2)
        assert_raises(AssertionError, var3.check_equivalence, var4)
        assert_raises(AssertionError, var3.check_equivalence, var5)
        assert_raises(AssertionError, var3.check_equivalence, var6)
        assert_raises(AssertionError, var4.check_equivalence, var1)
        assert_raises(AssertionError, var4.check_equivalence, var2)
        assert_raises(AssertionError, var4.check_equivalence, var3)
        assert_raises(AssertionError, var4.check_equivalence, var5)
        assert_raises(AssertionError, var5.check_equivalence, var1)
        assert_raises(AssertionError, var5.check_equivalence, var2)
        assert_raises(AssertionError, var5.check_equivalence, var3)
        assert_raises(AssertionError, var5.check_equivalence, var4)
        assert_raises(AssertionError, var5.check_equivalence, var6)
        assert_raises(AssertionError, var6.check_equivalence, var1)
        assert_raises(AssertionError, var6.check_equivalence, var2)
        assert_raises(AssertionError, var6.check_equivalence, var3)
        assert_raises(AssertionError, var6.check_equivalence, var5)
        
        ok_(var1 == var3)
        ok_(var3 == var1)
        ok_(var4 == var6)
        ok_(var6 == var4)
        
        ok_(var1 != var2)
        ok_(var1 != var4)
        ok_(var1 != var5)
        ok_(var1 != var6)
        ok_(var2 != var1)
        ok_(var2 != var3)
        ok_(var2 != var4)
        ok_(var2 != var5)
        ok_(var2 != var6)
        ok_(var3 != var2)
        ok_(var3 != var4)
        ok_(var3 != var5)
        ok_(var3 != var6)
        ok_(var4 != var1)
        ok_(var4 != var2)
        ok_(var4 != var3)
        ok_(var4 != var5)
        ok_(var5 != var1)
        ok_(var5 != var2)
        ok_(var5 != var3)
        ok_(var5 != var4)
        ok_(var5 != var6)
        ok_(var6 != var1)
        ok_(var6 != var2)
        ok_(var6 != var3)
        ok_(var6 != var5)
    
    def test_string_representation_without_namespace(self):
        var = VariablePlaceholder(u"aquí", None)
        eq_(unicode(var), u'Placeholder variable "aquí"')
        eq_(str(var), 'Placeholder variable "aquí"')
    
    def test_string_representation_with_namespace(self):
        var = VariablePlaceholder(u"aquí", ["some", "thing"])
        eq_(unicode(var), u'Placeholder variable "aquí" at some:thing')
        eq_(str(var), 'Placeholder variable "aquí" at some:thing')
    
    def test_representation_without_namespace(self):
        # With Unicode
        var = VariablePlaceholder(u"aquí", None)
        eq_(repr(var), '<Placeholder variable "aquí">')
        # With ASCII
        var = VariablePlaceholder("here", None)
        eq_(repr(var), '<Placeholder variable "here">')
    
    def test_representation_with_namespace(self):
        # With Unicode
        var = VariablePlaceholder(u"aquí", ["some", "thing"])
        eq_('<Placeholder variable "aquí" at namespace="some:thing">',
            repr(var))
        # With ASCII
        var = VariablePlaceholder("here", ["some", "thing"])
        eq_('<Placeholder variable "here" at namespace="some:thing">',
            repr(var))


class TestFunctionPlaceholder(object):
    """Tests for the FunctionPlaceholder."""
    
    def test_node_type(self):
        """Function placeholders are branch nodes."""
        func = FunctionPlaceholder("greet", None, String("arg0"))
        ok_(func.is_branch())
        assert_false(func.is_leaf())
    
    def test_constructor(self):
        """
        Function placeholders should contain an attribute which represents the
        name of the function in question and another one which represents the
        arguments passed.
        
        """
        func1 = FunctionPlaceholder(u"PAÍS", None)
        eq_(func1.name, u"país")
        eq_(func1.arguments, ())
        
        func2 = FunctionPlaceholder("country", None,
                                    FunctionPlaceholder("city", None),
                                    Number(2))
        eq_(func2.name, "country")
        eq_(func2.arguments, (FunctionPlaceholder("city", None), Number(2)))
    
    def test_no_namespace(self):
        """Function placeholders shouldn't have a default namespace."""
        func = FunctionPlaceholder("foo")
        eq_(len(func.namespace_parts), 0)
    
    def test_namespaces(self):
        """Function placeholders should be aware of their namespace."""
        func = FunctionPlaceholder("country", ["geo", "bar"])
        eq_(func.namespace_parts, ["geo", "bar"])
    
    def test_non_operands_as_arguments(self):
        """Function placeholders reject non-operands as arguments."""
        assert_raises(BadCallError, FunctionPlaceholder, "func", (),
                      Number(3), Number(6), 1)
        assert_raises(BadCallError, FunctionPlaceholder, "func", (), 2,
                      Number(6), Number(3))
        assert_raises(BadCallError, FunctionPlaceholder, "func", (),
                      Number(6), 3, Number(3))
    
    def test_no_operations(self):
        """Function placeholders don't support operations."""
        func = FunctionPlaceholder("func", ())
        assert_raises(InvalidOperationError, func.to_python)
        assert_raises(InvalidOperationError, func.get_logical_value)
        assert_raises(InvalidOperationError, func.equals, None)
        assert_raises(InvalidOperationError, func.less_than, None)
        assert_raises(InvalidOperationError, func.greater_than, None)
        assert_raises(InvalidOperationError, func.contains, None)
        assert_raises(InvalidOperationError, func.is_subset, None)
    
    def test_equivalence(self):
        """
        Two function placeholders are equivalent if they have the same name
        and share the namespace.
        
        """
        func1 = FunctionPlaceholder("foo", None, String("hi"), Number(4))
        func2 = FunctionPlaceholder("foo", None)
        func3 = FunctionPlaceholder("Foo", None, String("hi"), Number(4))
        func4 = FunctionPlaceholder("Foo", None, Number(4), String("hi"))
        func5 = FunctionPlaceholder("baz", None, String("hi"), Number(4))
        func6 = FunctionPlaceholder("foo", ["a", "b"], String("hi"), Number(4))
        func7 = FunctionPlaceholder("foo", ["a", "b"], String("hi"), Number(4))
        func8 = FunctionPlaceholder("foo", ["a", "b"])
        
        func1.check_equivalence(func3)
        func3.check_equivalence(func1)
        func6.check_equivalence(func7)
        func7.check_equivalence(func6)
        
        assert_raises(AssertionError, func1.check_equivalence, func2)
        assert_raises(AssertionError, func1.check_equivalence, func4)
        assert_raises(AssertionError, func1.check_equivalence, func5)
        assert_raises(AssertionError, func1.check_equivalence, func6)
        assert_raises(AssertionError, func1.check_equivalence, func7)
        assert_raises(AssertionError, func1.check_equivalence, func8)
        assert_raises(AssertionError, func2.check_equivalence, func1)
        assert_raises(AssertionError, func2.check_equivalence, func3)
        assert_raises(AssertionError, func2.check_equivalence, func4)
        assert_raises(AssertionError, func2.check_equivalence, func5)
        assert_raises(AssertionError, func2.check_equivalence, func6)
        assert_raises(AssertionError, func2.check_equivalence, func7)
        assert_raises(AssertionError, func2.check_equivalence, func8)
        assert_raises(AssertionError, func3.check_equivalence, func2)
        assert_raises(AssertionError, func3.check_equivalence, func4)
        assert_raises(AssertionError, func3.check_equivalence, func5)
        assert_raises(AssertionError, func3.check_equivalence, func6)
        assert_raises(AssertionError, func3.check_equivalence, func7)
        assert_raises(AssertionError, func3.check_equivalence, func8)
        assert_raises(AssertionError, func4.check_equivalence, func1)
        assert_raises(AssertionError, func4.check_equivalence, func2)
        assert_raises(AssertionError, func4.check_equivalence, func3)
        assert_raises(AssertionError, func4.check_equivalence, func5)
        assert_raises(AssertionError, func4.check_equivalence, func6)
        assert_raises(AssertionError, func4.check_equivalence, func7)
        assert_raises(AssertionError, func4.check_equivalence, func8)
        assert_raises(AssertionError, func5.check_equivalence, func1)
        assert_raises(AssertionError, func5.check_equivalence, func2)
        assert_raises(AssertionError, func5.check_equivalence, func3)
        assert_raises(AssertionError, func5.check_equivalence, func4)
        assert_raises(AssertionError, func5.check_equivalence, func6)
        assert_raises(AssertionError, func5.check_equivalence, func7)
        assert_raises(AssertionError, func5.check_equivalence, func8)
        assert_raises(AssertionError, func6.check_equivalence, func1)
        assert_raises(AssertionError, func6.check_equivalence, func2)
        assert_raises(AssertionError, func6.check_equivalence, func3)
        assert_raises(AssertionError, func6.check_equivalence, func4)
        assert_raises(AssertionError, func6.check_equivalence, func5)
        assert_raises(AssertionError, func6.check_equivalence, func8)
        assert_raises(AssertionError, func7.check_equivalence, func1)
        assert_raises(AssertionError, func7.check_equivalence, func2)
        assert_raises(AssertionError, func7.check_equivalence, func3)
        assert_raises(AssertionError, func7.check_equivalence, func4)
        assert_raises(AssertionError, func7.check_equivalence, func5)
        assert_raises(AssertionError, func7.check_equivalence, func8)
        assert_raises(AssertionError, func8.check_equivalence, func1)
        assert_raises(AssertionError, func8.check_equivalence, func2)
        assert_raises(AssertionError, func8.check_equivalence, func3)
        assert_raises(AssertionError, func8.check_equivalence, func4)
        assert_raises(AssertionError, func8.check_equivalence, func5)
        assert_raises(AssertionError, func8.check_equivalence, func6)
        assert_raises(AssertionError, func8.check_equivalence, func7)
        
        ok_(func1 == func3)
        ok_(func3 == func1)
        ok_(func6 == func7)
        ok_(func7 == func6)
        
        ok_(func1 != func2)
        ok_(func1 != func4)
        ok_(func1 != func5)
        ok_(func1 != func6)
        ok_(func1 != func7)
        ok_(func1 != func8)
        ok_(func2 != func1)
        ok_(func2 != func3)
        ok_(func2 != func4)
        ok_(func2 != func5)
        ok_(func2 != func6)
        ok_(func2 != func7)
        ok_(func2 != func8)
        ok_(func3 != func2)
        ok_(func3 != func4)
        ok_(func3 != func5)
        ok_(func3 != func6)
        ok_(func3 != func7)
        ok_(func3 != func8)
        ok_(func4 != func1)
        ok_(func4 != func2)
        ok_(func4 != func3)
        ok_(func4 != func5)
        ok_(func4 != func6)
        ok_(func4 != func7)
        ok_(func4 != func8)
        ok_(func5 != func1)
        ok_(func5 != func2)
        ok_(func5 != func3)
        ok_(func5 != func4)
        ok_(func5 != func6)
        ok_(func5 != func7)
        ok_(func5 != func8)
        ok_(func6 != func1)
        ok_(func6 != func2)
        ok_(func6 != func3)
        ok_(func6 != func4)
        ok_(func6 != func5)
        ok_(func6 != func8)
        ok_(func7 != func1)
        ok_(func7 != func2)
        ok_(func7 != func3)
        ok_(func7 != func4)
        ok_(func7 != func5)
        ok_(func7 != func8)
        ok_(func7 != func1)
        ok_(func7 != func2)
        ok_(func7 != func3)
        ok_(func7 != func4)
        ok_(func7 != func5)
        ok_(func7 != func8)
    
    def test_string_representation_without_namespace(self):
        func = FunctionPlaceholder(u"aquí", None, Number(1), Number(2))
        eq_(unicode(func), u'Placeholder function call "aquí"(1.0, 2.0)')
        eq_(str(func), 'Placeholder function call "aquí"(1.0, 2.0)')
    
    def test_string_representation_with_namespace(self):
        func = FunctionPlaceholder(u"aquí", ["a", "z"], Number(1), Number(2))
        eq_(unicode(func), u'Placeholder function call "aquí"(1.0, 2.0) at a:z')
        eq_(str(func), 'Placeholder function call "aquí"(1.0, 2.0) at a:z')
    
    def test_representation_without_namespace(self):
        # With Unicode:
        func = FunctionPlaceholder(u"aquí", None, Number(1), String("hi"))
        eq_('<Placeholder function call "aquí"(<Number 1.0>, <String "hi">)>',
            repr(func))
        # With ASCII:
        func = FunctionPlaceholder("here", None, Number(1), String("hi"))
        eq_(u'<Placeholder function call "here"(<Number 1.0>, <String "hi">)>',
            repr(func))
    
    def test_representation_with_namespace(self):
        # With Unicode:
        func = FunctionPlaceholder(u"aquí", ["a", "d"], Number(1), String("hi"))
        eq_('<Placeholder function call "aquí"(<Number 1.0>, <String "hi">) ' \
            'at namespace="a:d">',
            repr(func))
        # With ASCII:
        func = FunctionPlaceholder("here", ["a", "d"], Number(1), String("hi"))
        eq_(u'<Placeholder function call "here"(<Number 1.0>, <String "hi">) ' \
            'at namespace="a:d">',
            repr(func))


#}
