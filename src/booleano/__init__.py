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
Evaluation of boolean expressions in natural languages.

"""

class ExpressionsManager(object):
    
    def __init__(self, variables=[], var_containers={}, functions=[],
                 language=None):
        self.cache = {}
    
    def evaluate(self, expression, **helpers):
        # TODO: Check that all the helpers required by the variables have been
        # passed!
        pass
