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

import sys
import math
import blockdiag.DiagramDraw
from blockdiag.utils import XY
from blockdiag import noderenderer
from blockdiag import imagedraw


class DiagramDraw(blockdiag.DiagramDraw.DiagramDraw):
    def pagesize(self, scaled=False):
        width = self.diagram.width
        height = self.diagram.height + 1

        m = self.metrics
        margin = m.page_margin
        return XY((width + 5) * m.cellsize * 2 + margin.x * 2,
                  (height * 2 * m.cellsize * 2 + margin.y * 2))

    def draw(self, **kwargs):
        self._draw_background()

        if self.scale_ratio > 1:
            pagesize = self.pagesize(scaled=True)
            self.drawer.resizeCanvas(pagesize)

        for node in self.nodes:
            self.node(node, **kwargs)

    def _draw_background(self):
        metrics = self.metrics

        pagesize = self.pagesize()
        margin = metrics.page_margin
        for i in range(self.diagram.height + 2):
            height = margin.y + i * metrics.cellsize * 4
            _from = XY(margin.x, height)
            _to = XY(pagesize.x - margin.x, height)

            self.drawer.line((_from, _to), fill=self.fill)

        # left side of frame
        line = (XY(margin.x, margin.y), XY(margin.x, pagesize.y - margin.y))
        self.drawer.line(line, fill=self.fill)

        # right side of textbox
        line = (XY(margin.x + 10 * metrics.cellsize, margin.y),
                XY(margin.x + 10 * metrics.cellsize, pagesize.y - margin.y))
        self.drawer.line(line, fill=self.fill)

        # right side of frame
        line = (XY(pagesize.x - margin.x, margin.y),
                XY(pagesize.x - margin.x, pagesize.y - margin.y))
        self.drawer.line(line, fill=self.fill)

        for i in range(self.diagram.width - 1):
            width = margin.x + (i + 1 + 5) * metrics.cellsize * 2
            _from = XY(width, margin.y)
            _to = XY(width, pagesize.y - margin.y)

            self.drawer.line((_from, _to), fill='gray')

        # Smoothing back-ground images.
        if self.format == 'PNG':
            self.drawer.smoothCanvas()

    def node(self, node, **kwargs):
        m = self.metrics

        margin = m.page_margin
        top = margin.y + (node.xy.y + 1) * m.cellsize * 4
        bottom = top + m.cellsize * 4

        # textbox
        textbox = (margin.x, top, margin.x + m.cellsize * 10, bottom)
        self.drawer.textarea(textbox, node.label, fill=self.fill)

        width = margin.x + (node.xy.x + 5) * m.cellsize * 2
        if node.milestone:
            marker = (width, top, width + m.cellsize * 2, bottom)
            self.drawer.textarea(marker, "@", fill=self.fill)
        else:
            right = width + node.width * m.cellsize * 2
            line = (width, top + m.cellsize / 2,
                    right, bottom - m.cellsize / 2)
            self.drawer.rectangle(line, fill='lightblue', outline=self.fill)
