"""
This file is part of WSN-visor.

WSN-visor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

WSN-visor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with WSN-visor.  If not, see <http://www.gnu.org/licenses/>.
"""
#TODO: Add support for printing multigraphs edges with no, or reduced, overlapping.
import random, cairo, csv
from colors import *
from drawing import *


class display:
    self.drawCircle = {True: display.leaderCircle, False : display.standardCircle}

    def __init__(self):
        #Default configuration
        self.conf = {
            'width': 1024,
            'height': 1024,
            'bg_color': (0, 0, 0),
            'big_leaders': True,
            'bigger_factor': 3,
            'std_radius': 0.005,
            'random_pos': True,
            'random_colors': True,
            'show_id': True,
            'id_font': ('Georgia', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
            'id_font_size': 0.02,
            'png': True
        }

        self.colorpick = [AirForceBlue, Alizarin, Amber, AppleGreen, ArmyGreen, Asparagus, Banana, BlueViolet, Burgundy, Bubblegum, Byzantine, Camel, CarrotOrange, InchWorm, Olive]
        self.assignedRandColor = dict()
        self.colorAssign = dict()
        self.msg = dict()
        random.seed()

    def setMsg(self, msgName, edgeColor = (1, 1, 1), edgeWidth = drawing.MEDIUM_LINE, displayLabel = False, font = ('Georgia', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD), fontSize = 0.014, fontColor = (1, 1, 1)):
        """ Sets the parameters for painting a specific kind of message

        Keyword arguments:
        msgName --- String with the message kind.
        edgeColor --- Tuple of (r,g,b), each value ranging from 0 to 1, like those returned by the methos in the colors module.
        edgeWidth --- Floating point number that indicates the line width of the edge. There are some widths defined in the drawing module, eg, MEDIUM_LINE
        displayLabel --- Boolean that defines wheter to show the message id or not.
        font --- Tuple with font name, cairo font slant and cairo wight.
        fontSize --- Float with the size of the label letters.
        fontColor --- The font color expressed in a rgb tuple. """
        self.msg[msgName] = {
            'edge_color': edgeColor,
            'width': edgeWidth,
            'show_label': displayLabel,
            'label_font': font,
            'label_font_size': fontSize,
            'label_color': fontColor
        }

    def setPos(self, posDict):
        if getattr(posDict, 'keys'):
            self.pos = posDict
            self.conf['random_pos'] = False
        else:
            self.pos = dict()
            try:
                f = open(posDict, 'ro')
                reader = csv.reader(f, delimiter = ' ')
                for row in reader:
                    self.pos[row[0]] = (float(row[1]), float(row[2]))
                f.close()
                self.conf['random_pos'] = False
            except IOError:
                self.conf['random_pos'] = True


    def draw(self, g, pos, out):
        self.pos = pos
        context = surfaceCreate(self, self.conf['png'], self.conf['width'], self.conf['height'], self.conf['bg_color'], out)

        #Split edges by kind.
        edges = dict()
        for k in g.edges(keys = True):
            try:
                edges[k[2]].append(k)
            except:
                edges[k[2]] = list()
                edges[k[2]].append(k)

        for k in edges:
            showLabel = self.msg[k]['show_label']
            for e in edges[k]:
                drawEdge(context, self.pos[e[0]], self.pos[e[1]], self.msg[e[2]]['color'], self.msg[e[2]]['width'])
                if showLabel:
                    drawEdgeLabel(context, self.pos[e[0]], self.pos[e[1]], g.get_edge_data(*e)['label'], self.msg[e[2]]['color'], self.msg[e[2]]['font'], self.msg[e[2]]['font_size'])

        # After drawing the edges we draw the nodes themselves
        colors = self.colorpick[:]
        randColors = self.conf['random_colors']
        radius = self.conf['std_radius']
        leaderRadius = radius * self.conf['bigger_factor']
        colorAssign = self.colorAssign
        for n in g.nodes():
            try:
                isLeader = g.node[n]['leader']
            except KeyError:
                isLeader = False
            try:
                groupId = g.node[n]['group']
            except KeyError:
                try:
                    groupId = getattr(n, '__str__')()
                except AttributeError:
                    groupId = str(n)[-10:-1]
            try:
                drawNode(context, self.pos[n], colorAssign[groupId], leaderRadius if isLeader else radius)
            except KeyError:
                if randColors:
                    colorAssign[groupId] = randColor()
                else:
                    colorAssign[groupId] = colors.pop()()
                drawNode(context, self.pos[n], colorAssign[groupId], leaderRadius if isLeader else radius)

            if self.conf['show_id']:
                drawNodeId(self.c, pos, leaderRadius if isLeader else radius, node)

        if self.conf['png']:
            context.translate (0.1, 0.1) # Changing the current transformation matrix
            self.surface.write_to_png(out) # Output to PNG
