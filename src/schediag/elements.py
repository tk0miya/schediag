# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
import sys
from datetime import date
import blockdiag.elements
from blockdiag.elements import *
from blockdiag.utils.XY import XY


def str2date(_date):
    parts = _date.split('/')
    if len(parts) == 2:
        today = date.today()
        obj = date(today.year, int(parts[0]), int(parts[1]))
    elif len(parts) == 3:
        obj = date(*[int(p) for p in parts])
    else:
        raise

    return obj


class DiagramNode(blockdiag.elements.DiagramNode):
    def __init__(self, id):
        super(DiagramNode, self).__init__(id)
        self._from = None
        self._to = None
        self.milestone = False

    def set_term(self, term):
        if isinstance(term, (str, unicode)):
            self._from = str2date(term)
            self.milestone = True
        else:
            self._from = str2date(term[0])
            to = str2date(term[1])
            if to < self._from:
                to = date(to.year + 1, to.month, to.day)
            self._to = to
