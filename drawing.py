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
from math import pi
import cairo

THIN_LINE = 0.001
MEDIUM_LINE = 0.0025
THICK_LINE = 0.005
CIRCLE_LINE = 0.006

def surfaceCreate(self, png, width, height, bg_color, o):
    if png:
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    else:
        self.surface = cairo.SVGSurface(o, width, height)
    context = cairo.Context (self.surface)
    context.scale(width-50, height-50) # Normalizing the canvas
    drawBg(width, height, *bg_color)
    context.translate(0.015, 0.015)
    return context

#Empty circle for leaders (Sepia Color)
def drawCircle(context, pos, rad, color):
    #context.set_source_rgb(0.44, 0.26, 0.08)
    context.set_source_rgb(*color)
    context.set_line_width(CIRCLE_LINE)
    context.arc(pos[0], pos[1], rad/2.0, 0, 2*pi)
    context.stroke()

def drawNodeId(context, pos, rad, nodeId, font = ('Georgia', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)):
    context.select_font_face(*font)
    context.set_font_size(0.02)
    context.move_to(pos[0]+2*rad, pos[1])
    context.show_text(hex(nodeId))
    context.stroke()


def drawNode(context, pos, nodeId, color, rad = 0.005):
    """ Draws a node according to the passed parameters.

    Keyword arguments:
    context --- The cairo context object in which to draw.
    pos --- A two item tuple for x y positions, each value ranging 0..1.
    nodeId --- The node object or its id (can be set in the node dictionary of networkx).
    color --- A three item tuple for rgb, each value ranging 0..1.
    rad --- Radius of the node circle representation.
    isLeader --- True if the node is leader, False otherwise. """
    drawCircle(context, pos, rad, color)
    context.set_source_rgb(color)

    #Filling circle
    context.set_line_width(0.003)
    context.arc(pos[0], pos[1], rad/1.2, 0, 2*pi)
    context.fill()

def drawBg(context, width, height, color):
    context.set_source_rgb(*color)
    context.rectangle (0, 0, width, height)
    context.fill ()

def drawEdge(context, posOrig, posTarg, color, width):
    context.set_source_rgb(*color)
    context.set_line_width(width)
    context.move_to(posOrig[0], posOrig[1])
    context.line_to(posTarg[0], posTarg[1])
    context.stroke()

def drawEdgeLabel(context, posOrig, posTarg, text, color, font = ('Georgia', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD), fontSize = 0.014):
    context.set_source_rgb(*color)
    context.select_font_face(*font)
    context.set_font_size(fontSize)
    context.move_to((posOrig[0]+posTarg[0])*1.0/2,(posOrig[1]+posTarg[1])*1.0/2)
    context.show_text(text)
    context.stroke()
