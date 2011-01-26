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
Generic Pyparsing helpers.

These helpers are Booleano-independent. Feel free to copy any of them into
your project, this is freedomware!

TODO: This module is far from finished.

"""

from pyparsing import (FollowedBy, Forward, Group, NoMatch, Optional, Suppress)

__all__ = ("make_operations", )


#{ Operation precedence utilities


def make_operations(operand, operators, group_start="(",  group_end=")"):
    """
    Build the Pyparsing grammar for the ``operators`` and return it.
    
    :param operand: The Pyparsing grammar for the operand to be handled by
        the ``operators``.
    :param operators: List of quintuples that define the properties of every
        operator.
    
    The order of the ``operators`` describe the precedence of the operators.
    
    Each tuple in ``operators`` are made up of the following five elements,
    which define the operator:
    
    - The Pyparsing expression for the operator.
    - The arity of the operator (1 or 2).
    - The associativity of the operator ("left" or "right"), if it's a binary
      operation; otherwise ``None``.
    - The notation of the operator (prefix, postfix or infix), if it's a binary
      one.
    - Whether the left-hand operand should be the master operand. If ``False``,
      the left- and right-hand operands will be the slave and master ones.
    - The parse action of the operator.
    
    The parse actions for unary operations will receive the named results for 
    the ``operator`` and the ``operand``, while those for binary operations will
    receive the named results for the ``operator`` and the ``master_operand``
    and the ``slave_operand``.
    
    The code for the operatorPrecedence() function in Pyparsing was used as an
    starting point to make this function.
    
    """
    operation = Forward()
    group_start = Suppress(group_start)
    group_end = Suppress(group_end)
    last_expression = operand | (group_start + operation + group_end)
    
    # The "previous_operators" variable represents the expressions for the
    # previous operators, so it can be used to prevent wrong matches of
    # operators when a higher level operator was expected. This would happen
    # when the string of an operator represents the starting characters of
    # a higher level operator. See Bug #397807.
    previous_operators = NoMatch()
    
    for (operator_expr, arity, assoc, notation, master_left, pa) in operators:
        final_operator = ~previous_operators + operator_expr
        new_expression = _append_operation(operand, last_expression,
                                           final_operator, arity, assoc.lower(),
                                           notation.lower(), master_left, pa)
        last_expression = new_expression
        # Updating the list of previous operators, so they won't be matched in
        # higher-level operations:
        previous_operators = previous_operators | operator_expr
    
    operation << last_expression
    return operation


def _append_operation(operand, last_expression, operator_expr, arity,
                      associativity, master_left, notation):
    """
    Return the ``last_expression`` with the operation described by the arguments
    appended.
    
    """
    # TODO: Use the "master_left" variable.
    new_expression = Forward()
    
    operator_expr = operator_expr.setResultsName("operator")
    
    if arity == 1:
        if notation == "prefix":
            # Syntax: <OPERATOR> <OPERAND>
            if not isinstance(operator_expr, Optional):
                # Trying to avoid LR
                operator_expr = Optional(operator_expr)
            operation = (
                FollowedBy(operator_expr.expr + new_expression) +
                Group(operator_expr.setResultsName("operand") + new_expression)
                )
        elif notation == "postfix":
            # Syntax: <OPERAND> <OPERATOR>
            operation = (
                FollowedBy(last_expression + operator_expr) +
                Group(last_expression.setResultsName("operand") +
                      OneOrMore(operator_expr))
                )
        else:
            raise ValueError("Infix notation is not supported for unary "
                             "operators")
    
    elif arity == 2:
        # TODO: Add the parse results "left_operand" and "right_operand".
        if associativity not in ("left", "right"):
            raise ValueError("Operations must indicate right or left "
                             "associativity")
        
        if notation == "prefix":
            # Syntax: <OPERATOR> <LEFT_OPERAND> <RIGHT_OPERAND>
            # TODO:
            pass
        elif notation == "postfix":
            # Syntax: <LEFT_OPERAND> <RIGHT_OPERAND> <OPERATOR>
            # TODO:
            pass
        elif notation == "infix":
            # Syntax: <LEFT_OPERAND> <OPERATOR> <RIGHT_OPERAND>
            if associativity == "left":
                operation = (
                    FollowedBy(last_expression + operator_expr + last_expression) 
                    +
                    Group(last_expression +
                          OneOrMore(operator_expr + last_expression))
                    )
            else:
                operation = (
                    FollowedBy(last_expression + operator_expr + new_expression)
                    +
                    Group(last_expression +
                          OneOrMore(operator_expr + new_expression))
                    )
        else:
            raise ValueError('Unknown notation "%s"' % notation)
    
    else:
        raise ValueError("Only unary and binary operators are supported")
    
    operation.setParseAction(parse_action)
    new_expression << (operation | last_expression)
    
    return operation


#}
