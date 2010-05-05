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
Booleano classes.

There are two types of Booleano classes:
 - Variable.
 - Function.

**Python classes and Booleano classes are two different things!**

"""
from booleano.nodes.operands import Operand

__all__ = ["Variable"]


class Class(Operand):
    """
    Base class for Booleano's anonymous classes.
    
    The classes are anonymous because the have no notion of binding. From the
    Wikipedia:
    
        In most languages, a class is bound to a name or identifier upon
        definition. However, some languages allow classes to be defined without
        names. Such a class is called an anonymous class (analogous to named vs.
        anonymous functions).
    
    """
    
    # Only actual classes should be checked.
    bypass_operation_check = True


class Variable(Class):
    """
    Developer-defined variable.
    
    """
    
    # Only actual variables should be checked.
    bypass_operation_check = True
    
    def __unicode__(self):
        """Return the Unicode representation of this variable."""
        return 'Anonymous variable [%s]' % self.__class__.__name__
    
    def __repr__(self):
        """Represent this variable."""
        return "<Anonymous variable [%s]>" % self.__class__.__name__

