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
Supported operations represented in Python objects.

Once parsed, the binary expressions are turned into the relevant operation
using the classes provided by this package.

"""

__all__ = ["OPERATIONS"]


# Byte flag for the base operations:
OPERATIONS = set((
    "equality",           # ==, !=
    "inequality",         # >, <
    "boolean",            # is it met or not?
    "membership",         # does SetX contain ItemY?
))

