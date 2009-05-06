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
Tokens used by the parser.

"""

# Default, generic operators. To keep things simple, we're not going to
# implement the NAND and NOR operators.
OPERATORS = {
    'NOT': "~",
    'AND': "&",
    'OR': "|",
    'XOR': "^",
    'IN': u"∈",
    'CONTAINED': u"⊂",
}


#}
