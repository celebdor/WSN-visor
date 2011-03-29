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

import math, random, cairo, csv
from colors import *

pi = math.pi

class display:
    def __init__(self):
        #Default configuration
        self.conf = {'width': 1024, 'height': 1024, 'big_leaders': True, 'random_pos': True, 'random_colors': True, 'show_id': True, 'show_label': True, 'png': True, 'bg_color': (0, 0, 0) }

        self.drawCircle = {True: self.leaderCircle, False : self.standardCircle}
        self.edgeColor = {'msg': setBlueViolet, 'highway': setAppleGreen, 'cluster': setWhite}
        self.edgeWidth = {'msg': self.setThin, 'highway': self.setThick, 'cluster': self.setMedium}
        self.colorpick = [setAirForceBlue, setAlizarin, setAmber, setAppleGreen, setArmyGreen, setAsparagus, setBanana, setBlueViolet, setBurgundy, setBubblegum, setByzantine, setCamel, setCarrotOrange, setInchWorm, setOlive]
        self.randColor = dict()
        self.colorAssign = dict()
        self.msg = dict()
        random.seed()

    def setMsg(self, msgName, edgeColor, edgeWidth = setMedium, displayLabel = False):
        self.msg[msgName] = {'edgeColor': edgeColor, 'edgeWidth': edgeWidth, 'displayLabel': displayLabel}

    def setPos(self, posDict):
        self.pos = dict()
        if getattr(posDict, 'keys'):
            self.pos = posDict
            self.conf['random_pos'] = False
        else:
            try:
                f = open(posDict, 'ro')
                reader = csv.reader(f, delimiter = ' ')
                for row in reader:
                    self.pos[row[0]] = (float(row[1]), float(row[2]))
                f.close()
                self.conf['random_pos'] = False
            except IOError:
                self.conf['random_pos'] = True

    def surfaceCreate(self, png, o):
        if self.conf['png']:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.conf['width'], self.conf['height'])
        else:
            self.surface = cairo.SVGSurface(o, self.conf['width'], self.conf['height'])
        self.c = cairo.Context (self.surface)
        self.c.scale(self.conf['width']-50, self.conf['height']-50) # Normalizing the canvas
        self.drawBg(*self.conf['bg_color'])
        self.c.translate(0.015, 0.015)

    def setThin(self):
        self.c.set_line_width(0.001)

    def setThick(self):
        self.c.set_line_width(0.005)

    def setMedium(self):
        self.c.set_line_width(0.0025)

    def setCircleWidth(self):
        self.c.set_line_width(0.006)


    def drawNodeId(self, x, y, rad, id):
        c = self.c
        c.select_font_face('Georgia', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(0.02)
        c.move_to(x+2*rad, y)
        c.show_text(hex(id))
        c.stroke()

    #Empty circle for leaders (Sepia Color)
    def leaderCircle(self, x, y, rad):
        c = self.c
        c.set_source_rgb(0.44, 0.26, 0.08)
        self.setCircleWidth()
        c.arc(x, y, rad/2.0, 0, 2*pi)
        c.stroke()

    #Empty circle for regular ports (White)
    def standardCircle(self, x, y, rad):
        c = self.c
        c.set_source_rgb(1, 1, 1)
        self.setCircleWidth()
        c.arc(x, y, rad/2.0, 0, 2*pi)
        c.stroke()

    def drawNode(self, n, rad, k, color):
        if self.conf['random_pos']:
            pos = self.pos[n]
        else:
            pos = self.pos[n.id]
        if self.conf['bigger_leaders'] and k:
            rad*=3
        self.drawCircle[k](pos[0], pos[1], rad)
        if self.conf['random_colors']:
            color(self.c, self.randColor[n.sid])
        else:
            color(self.c)

        if self.conf['show_id']:
            self.drawNodeId(pos[0], pos[1], rad, n.id)

        #Filling circle
        c = self.c
        c.set_line_width(0.003)
        c.arc(pos[0], pos[1], rad/1.2, 0, 2*pi)
        c.fill()

    def drawBg(self, r, g, b):
        c = self.c
        c.set_source_rgb(r, g, b)
        c.rectangle (0, 0, self.width, self.height) # Rectangle(x0, y0, x1, y1)
        c.fill ()

    def drawEdge(self, o, t, k):
        if self.conf['random_pos']:
            pos_a = self.pos[o]
            pos_b = self.pos[t]
        else:
            pos_a = self.pos[o.id]
            pos_b = self.pos[t.id]
        c = self.c
        self.edgeColor[k]()
        self.edgeWidth[k]()
        c.move_to(pos_a[0], pos_a[1])
        c.line_to(pos_b[0], pos_b[1])
        c.stroke()

    def drawEdgeLabel(self, o, t, text ):
        if self.conf['random_pos']:
            pos_a = self.pos[o]
            pos_b = self.pos[t]
        else:
            pos_a = self.pos[o.id]
            pos_b = self.pos[t.id]
        c = self.c
        self.edgeColor['msg']()
        c.select_font_face('Georgia', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(0.014)
        c.move_to((pos_a[0]+pos_b[0])*1.0/2,(pos_a[1]+pos_b[1])*1.0/2)
        c.show_text(text)
        c.stroke()

    def draw(self, g, pos, out):
        self.pos = pos

        self.surfaceCreate(self.conf['png'], out)

        #After this step draw lines between nodes and parent id in a new iteration
        edges = dict()
        for k in g.edges(keys = True):
            try:
                edges[k[2]].append(k)
            except:
                edges[k[2]] = list()
                edges[k[2]].append(k)

        #First we draw the cluster edges
        if edges.has_key('cluster'):
            for k in edges['cluster']:
                self.drawEdge(k[0], k[1], k[2])

        #Then we draw the highways
        if edges.has_key('highway'):
            for k in edges['highway']:
                self.drawEdge(k[0], k[1], k[2])

        #Finally we draw the message edges
        show_label = self.conf['show_label']
        if edges.has_key('msg'):
            for k in edges['msg']:
                self.drawEdge(k[0], k[1], k[2])
                if show_label:
                    self.drawEdgeLabel(k[0], k[1], g.get_edge_data(*k)['label'])

        # After drawing the lines we draw the nodes themselves
        # Set initial color in a random way (We are tired of the same colors all the time)
        colors = self.colorpick[:]
        randColors = self.conf['random_colors']
        colorAssign = self.colorAssign
        for n in g.nodes():
            try:
                self.drawNode(n, 0.005, n.isLeader(), colorAssign[n.sid] )
            except:
                if randColors:
                    colorAssign[n.sid] = getRandColor
                    r = random.randint( 0, 0xFFFFFF )
                    self.randColor[n.sid] = ( (((r>>16)&0xFF)*1.0/255, ((r>>8)&0xFF)*1.0/255, (r&0xFF)*1.0/255 ) )
                else:
                    colorAssign[n.sid] = colors.pop()
                self.drawNode(n, 0.005, n.isLeader() , colorAssign[n.sid] )

        if self.conf['png']:
            self.c.translate (0.1, 0.1) # Changing the current transformation matrix
            self.surface.write_to_png(out) # Output to PNG

