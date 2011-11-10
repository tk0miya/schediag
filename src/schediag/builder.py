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

import math
from elements import *
import diagparser
from blockdiag.utils import XY


class DiagramTreeBuilder:
    def build(self, tree):
        self.diagram = Diagram()
        self.diagram = self.instantiate(self.diagram, tree)

        _min = min(n._to or n._from for n in self.diagram.nodes)
        _max = max(n._to or n._from for n in self.diagram.nodes)

        self.diagram.width = (_max - _min).days + 1
        self.diagram.height = len(self.diagram.nodes)
        for i, node in enumerate(self.diagram.nodes):
            node.xy = XY((node._from - _min).days, i)

            if node._to:
                node.width = (node._to - node._from).days + 1
            else:
                node.width = 1

        return self.diagram

    def append_node(self, node, group):
        if node not in self.diagram.nodes:
            self.diagram.nodes.append(node)

        if isinstance(group, NodeGroup) and node not in group.nodes:
            if node.group:
                msg = "DiagramNode could not belong to two groups"
                raise RuntimeError(msg)

            group.nodes.append(node)
            node.group = group

    def instantiate(self, group, tree):
        for stmt in tree.stmts:
            if isinstance(stmt, diagparser.Node):
                node = DiagramNode.get(stmt.id)
                node.set_attributes(stmt.attrs)
                self.append_node(node, group)

            elif isinstance(stmt, diagparser.DefAttrs):
                #group.set_attributes(stmt.attrs)

                for attr in stmt.attrs:
                    node = DiagramNode.get(attr.name)
                    node.set_term(attr.value)
                    self.append_node(node, group)

            else:
                raise AttributeError("Unknown sentense: " + str(type(stmt)))

        return group


class ScreenNodeBuilder:
    @classmethod
    def build(klass, tree):
        DiagramNode.clear()
        DiagramEdge.clear()
        NodeGroup.clear()
        Diagram.clear()

        return DiagramTreeBuilder().build(tree)
