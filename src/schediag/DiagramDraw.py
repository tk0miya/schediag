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
from blockdiag.utils.XY import XY
from blockdiag import noderenderer
from blockdiag import imagedraw


class DiagramDraw(object):
    MetrixClass = None

    @classmethod
    def set_metrix_class(cls, MetrixClass):
        cls.MetrixClass = MetrixClass

    def __init__(self, format, diagram, filename=None, **kwargs):
        self.format = format.upper()
        self.diagram = diagram
        self.fill = kwargs.get('fill', (0, 0, 0))
        self.badgeFill = kwargs.get('badgeFill', 'pink')
        self.font = kwargs.get('font')
        self.filename = filename

        if self.format == 'PNG' and kwargs.get('antialias'):
            self.scale_ratio = 2
        else:
            self.scale_ratio = 1
        self.metrix = self.MetrixClass(kwargs.get('basediagram', diagram),
                                       scale_ratio=self.scale_ratio, **kwargs)

        kwargs = dict(font=self.font,
                      nodoctype=kwargs.get('nodoctype'),
                      scale_ratio=self.scale_ratio)

        if self.format == 'PNG':
            self.shadow = kwargs.get('shadow', (64, 64, 64))
        else:
            self.shadow = kwargs.get('shadow', (0, 0, 0))

        self.drawer = imagedraw.create(self.format, self.filename,
                                       self.pagesize(), **kwargs)

    @property
    def nodes(self):
        return self.diagram.nodes

    @property
    def groups(self):
        return []

    @property
    def edges(self):
        return []

    def pagesize(self, scaled=False):
        if scaled:
            metrix = self.metrix
        else:
            metrix = self.metrix.originalMetrix()

        width = self.diagram.width
        height = self.diagram.height + 1

        margin = metrix.pageMargin
        return XY((width + 5) * metrix.cellSize * 2 + margin.x * 2,
                  (height * 2 * metrix.cellSize * 2 + margin.y * 2))

    def draw(self, **kwargs):
        self._draw_background()

        if self.scale_ratio > 1:
            pagesize = self.pagesize(scaled=True)
            self.drawer.resizeCanvas(pagesize)

        for node in self.nodes:
            self.node(node, **kwargs)

    def _draw_background(self):
        metrix = self.metrix.originalMetrix()

        pagesize = self.pagesize()
        margin = metrix.pageMargin
        for i in range(self.diagram.height + 2):
            height = margin.y + i * metrix.cellSize * 4
            _from = XY(margin.x, height)
            _to = XY(pagesize.x - margin.x, height)

            self.drawer.line((_from, _to), fill=self.fill)

        # left side of frame
        line = (XY(margin.x, margin.y), XY(margin.x, pagesize.y - margin.y))
        self.drawer.line(line, fill=self.fill)

        # right side of textbox
        line = (XY(margin.x + 10 * metrix.cellSize, margin.y),
                XY(margin.x + 10 * metrix.cellSize, pagesize.y - margin.y))
        self.drawer.line(line, fill=self.fill)

        # right side of frame
        line = (XY(pagesize.x - margin.x, margin.y),
                XY(pagesize.x - margin.x, pagesize.y - margin.y))
        self.drawer.line(line, fill=self.fill)

        for i in range(self.diagram.width - 1):
            width = margin.x + (i + 1 + 5) * metrix.cellSize * 2
            _from = XY(width, margin.y)
            _to = XY(width, pagesize.y - margin.y)

            self.drawer.line((_from, _to), fill='gray')

        # Smoothing back-ground images.
        if self.format == 'PNG':
            self.drawer.smoothCanvas()

    def node(self, node, **kwargs):
        m = self.metrix

        margin = m.pageMargin
        top = margin.y + (node.xy.y + 1) * m.cellSize * 4
        bottom = top + m.cellSize * 4

        # textbox
        textbox = (margin.x, top, margin.x + m.cellSize * 10, bottom)
        self.drawer.textarea(textbox, node.label, fill=self.fill,
                             font=self.font, fontsize=self.metrix.fontSize)

        width = margin.x + (node.xy.x + 5) * m.cellSize * 2
        if node.milestone:
            marker = (width, top, width + m.cellSize * 2, bottom)
            self.drawer.textarea(marker, "@", fill=self.fill,
                                 font=self.font, fontsize=self.metrix.fontSize)
        else:
            right = width + node.width * m.cellSize * 2
            line = (width, top + m.cellSize / 2,
                    right, bottom - m.cellSize / 2)
            self.drawer.rectangle(line, fill='lightblue', outline=self.fill)

    def save(self, filename=None, size=None):
        if filename:
            self.filename = filename

            msg = "WARNING: DiagramDraw.save(filename) was deprecated.\n"
            sys.stderr.write(msg)

        return self.drawer.save(self.filename, size, self.format)


from blockdiag.DiagramMetrix import DiagramMetrix
DiagramDraw.set_metrix_class(DiagramMetrix)
