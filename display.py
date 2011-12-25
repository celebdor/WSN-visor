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

import math, random
import cairo
from functools import partial

class Display:
    """Rendering class of the WSN-Visor"""
    def __init__(self):
        """Initializer"""
        #Default topology sizes
        self.width = 1024
        self.height = 1024

        self.draw_circle = {True: partial(self.drawing_circle,
                                          0.44, 0.26, 0.08),
                            False : partial(self.drawing_circle,
                                          1.00, 1.00, 1.00)}
        self.edge_color = {'msg': partial(self.set_cairo_color,
                                          0.54, 0.17, 0.89),
                           'highway': partial(self.set_cairo_color,
                                              0.55, 0.71, 0.00),
                           'cluster': partial(self.set_cairo_color,
                                              1.00, 1.00, 1.00)}
        self.edge_witdth = {'msg': partial(self.set_line_width, 0.001),
                            'highway': partial(self.set_line_width, 0.005),
                            'cluster': partial(self.set_line_width, 0.0025)}
        # Colors:
        # air force blue, alizarin, amber, apple_green, army_green,
        # asparagus, banana, blue_purple, burgundy, bubblegum, byzantine,
        # camel, carrot_orange, inch worm, olive
        self.colorpick = [partial(self.set_cairo_color, 0.36, 0.54, 0.66),
                          partial(self.set_cairo_color, 0.89, 0.15, 0.21),
                          partial(self.set_cairo_color, 1.00, 0.75, 0.00),
                          partial(self.set_cairo_color, 0.55, 0.71, 0.00),
                          partial(self.set_cairo_color, 0.29, 0.33, 0.13),
                          partial(self.set_cairo_color, 0.53, 0.66, 0.42),
                          partial(self.set_cairo_color, 1.00, 0.82, 0.16),
                          partial(self.set_cairo_color, 0.54, 0.17, 0.89),
                          partial(self.set_cairo_color, 0.50, 0.00, 0.13),
                          partial(self.set_cairo_color, 0.99, 0.76, 0.80),
                          partial(self.set_cairo_color, 0.74, 0.20, 0.64),
                          partial(self.set_cairo_color, 0.76, 0.40, 0.62),
                          partial(self.set_cairo_color, 0.93, 0.57, 0.13),
                          partial(self.set_cairo_color, 0.70, 0.93, 0.36),
                          partial(self.set_cairo_color, 0.50, 0.50, 0.00)]
        self.pos = None
        self.surface = None
        self.context = None
        self.options = None
        self.rand_color = dict()
        self.color_assign = dict()
        random.seed()

    def surface_create(self, png, output_file):
        """Creates the canvas surface and context in cairo for the rendering"""
        if png == True:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width,
                                              self.height)
        else:
            self.surface = cairo.SVGSurface(output_file,
                                            self.width, self.height)
        self.context = cairo.Context(self.surface)
        # Normalizing the canvas
        self.context.scale(self.width-50, self.height-50)
        self.draw_bg(0, 0, 0)
        self.context.translate(0.015, 0.015)

    def set_line_width(self, width):
        """Sets the cairo drawing line width to width"""
        self.context.set_line_width(width)

    def set_cairo_color(self, red = 1.00, green = 0.82, blue = 0.16):
        """Sets the cairo drawing color to the rgb value. Defaults to banana
        yellow"""
        self.context.set_source_rgb(red, green, blue)

    def draw_node_id(self, pos_x, pos_y, rad, identifier):
        """Draws the node identifier beside the node circle"""
        cont = self.context
        cont.select_font_face('Georgia', cairo.FONT_SLANT_NORMAL,
                           cairo.FONT_WEIGHT_BOLD)
        cont.set_font_size(0.02)
        cont.move_to(pos_x+2*rad, pos_y)
        cont.show_text(hex(identifier))
        cont.stroke()

    def drawing_circle(self, red, green, blue, pos_x, pos_y, rad):
        """Draw the node representation as a circle"""
        cont = self.context
        cont.set_source_rgb(red, green, blue)
        cont.set_line_width(0.006)
        cont.arc(pos_x, pos_y, rad/2.0, 0, 2*math.pi)
        cont.stroke()

    def draw_node(self, node, rad, k, color):
        """Draws a node in the canvas with the appropriate options"""
        if self.options.rand_pos:
            pos = self.pos[node]
        else:
            pos = self.pos[node.id]
        if self.options.bigger_leaders and k:
            rad *= 3
        self.draw_circle[k](pos[0], pos[1], rad)
        if self.options.random_colors:
            color(*self.rand_color[node.sid])
        else:
            color()

        if self.options.show_id:
            self.draw_node_id(pos[0], pos[1], rad, node.id)

        #Filling circle
        cont = self.context
        cont.set_line_width(0.003)
        cont.arc(pos[0], pos[1], rad/1.2, 0, 2*math.pi)
        cont.fill()

    def draw_bg(self, red, green, blue):
        """Draws the background of the canvas """
        cont = self.context
        cont.set_source_rgb(red, green, blue)
        cont.rectangle (0, 0, self.width, self.height)
        cont.fill ()

    def draw_edge(self, origin, target, kind):
        """Draws an edge between the origin and the target nodes"""
        if self.options.rand_pos:
            pos_a = self.pos[origin]
            pos_b = self.pos[target]
        else:
            pos_a = self.pos[origin.id]
            pos_b = self.pos[target.id]
        cont = self.context
        self.edge_color[kind]()
        self.edge_witdth[kind]()
        cont.move_to(pos_a[0], pos_a[1])
        cont.line_to(pos_b[0], pos_b[1])
        cont.stroke()

    def draw_edge_label(self, origin, target, text):
        """Draws the label of an edge beside said edge"""
        if self.options.rand_pos:
            pos_a = self.pos[origin]
            pos_b = self.pos[target]
        else:
            pos_a = self.pos[origin.id]
            pos_b = self.pos[target.id]
        cont = self.context
        self.edge_color['msg']()
        cont.select_font_face('Georgia', cairo.FONT_SLANT_NORMAL,
                           cairo.FONT_WEIGHT_BOLD)
        cont.set_font_size(0.014)
        cont.move_to((pos_a[0]+pos_b[0])*1.0/2,(pos_a[1]+pos_b[1])*1.0/2)
        cont.show_text(text)
        cont.stroke()

    def draw(self, graph, pos, out):
        """Main method of the display class that renders the graph"""
        self.pos = pos

        if self.options.yellow:
            self.edge_color['highway'] = self.set_cairo_color

        self.surface_create(self.options.save_to_png, out)

        # After this step draw lines between nodes and parent id in a new
        # iteration
        edges = dict()
        for k in graph.edges(keys = True):
            try:
                edges[k[2]].append(k)
            except KeyError:
                edges[k[2]] = list()
                edges[k[2]].append(k)

        #First we draw the cluster edges
        if edges.has_key('cluster'):
            for k in edges['cluster']:
                self.draw_edge(k[0], k[1], k[2])

        #Then we draw the highways
        if edges.has_key('highway'):
            for k in edges['highway']:
                self.draw_edge(k[0], k[1], k[2])

        #Finally we draw the message edges
        if edges.has_key('msg'):
            for k in edges['msg']:
                self.draw_edge(k[0], k[1], k[2])
                if self.options.show_label:
                    self.draw_edge_label(k[0], k[1],
                                         graph.get_edge_data(*k)['label'])

        # After drawing the lines we draw the nodes themselves
        # Set initial color in a random way (We are tired of the same colors
        # all the time)
        colors = self.colorpick[:]
        rand_colors = self.options.random_colors
        color_assign = self.color_assign
        for node in graph.nodes():
            try:
                self.draw_node(node, 0.005, node.is_leader(),
                               color_assign[node.sid])
            except KeyError:
                if rand_colors:
                    color_assign[node.sid] = self.set_cairo_color
                    rand_num = random.randint( 0, 0xFFFFFF )
                    self.rand_color[node.sid] = ((((rand_num>>16)&0xFF)*1.0/255,
                                              ((rand_num>>8)&0xFF)*1.0/255,
                                              (rand_num&0xFF)*1.0/255 ))
                else:
                    color_assign[node.sid] = colors.pop()
                self.draw_node(node, 0.005, node.is_leader(),
                               color_assign[node.sid])

        if self.options.save_to_png == True:
            # Changing the current transformation matrix and outputting to PNG
            self.context.translate (0.1, 0.1) 
            self.surface.write_to_png(out)

