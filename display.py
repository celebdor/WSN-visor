#!/usr/bin/env python

from optparse import OptionParser
import sys, math, re, random
import cairo

pi = math.pi

class display:
     def __init__(self):
          #Default topology sizes
          self.width = 1024
          self.height = 1024

          self.drawCircle = {True: self.leaderCircle, False : self.standardCircle}
          self.edgeColor = {'msg': self.setBlueViolet, 'highway': self.setAppleGreen, 'cluster': self.setWhite}
          self.edgeWidth = {'msg': self.setThin, 'highway': self.setThick, 'cluster': self.setMedium}
          self.colorpick = [self.setAirForceBlue, self.setAlizarin, self.setAmber, self.setAppleGreen, self.setArmyGreen, self.setAsparagus, self.setBanana, self.setBlueViolet, self.setBurgundy, self.setBubblegum, self.setByzantine, self.setCamel, self.setCarrotOrange, self.setInchWorm, self.setOlive]
          self.randColor = dict()
          self.colorAssign = dict()
          random.seed()

     def surfaceCreate(self, png, o):
          if png == True:
               self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
          else:
               self.surface = cairo.SVGSurface(o, self.width, self.height)
          self.c = cairo.Context (self.surface)
          self.c.scale(self.width-50, self.height-50) # Normalizing the canvas
          self.drawBg(0, 0, 0)
          self.c.translate(0.015, 0.015)

     def setThin(self):
          self.c.set_line_width(0.001)

     def setThick(self):
          self.c.set_line_width(0.005)

     def setMedium(self):
          self.c.set_line_width(0.0025)

     def setAirForceBlue(self):
          self.c.set_source_rgb(0.36, 0.54, 0.66)
     
     def getRandColor(self, col):
          self.c.set_source_rgb( *col )

     def setAlizarin(self):
          self.c.set_source_rgb(0.89, 0.15, 0.21)

     def setAmber(self):
          self.c.set_source_rgb(1.0, 0.75, 0.00)

     def setAppleGreen(self):
          self.c.set_source_rgb(0.55, 0.71, 0.00)

     def setArmyGreen(self):
          self.c.set_source_rgb(0.29, 0.33, 0.13)

     def setAsparagus(self):
          self.c.set_source_rgb(0.53, 0.66, 0.42)

     def setBanana(self):
          self.c.set_source_rgb(1.00, 0.82, 0.16)

     def setBlueViolet(self):
          self.c.set_source_rgb(0.54, 0.17, 0.89)

     def setBurgundy(self):
          self.c.set_source_rgb(0.50, 0.00, 0.13)

     def setBubblegum(self):
          self.c.set_source_rgb(0.99, 0.76, 0.80)

     def setByzantine(self):
          self.c.set_source_rgb(0.74, 0.20, 0.64)

     def setCamel(self):
          self.c.set_source_rgb(0.76, 0.40, 0.62)

     def setCarrotOrange(self):
          self.c.set_source_rgb(0.93, 0.57, 0.13)

     def setInchWorm(self):
          self.c.set_source_rgb(0.70, 0.93, 0.36)

     def setOlive(self):
          self.c.set_source_rgb(0.50, 0.50, 0.00)

     def setCircleWidth(self):
          self.c.set_line_width(0.006)

     def setWhite(self):
          self.c.set_source_rgb(1.00, 1.00, 1.00)

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
          if self.options.rand_pos:
               pos = self.pos[n]
          else:
               pos = self.pos[n.id]
          if self.options.bigger_leaders and k:
               rad*=3
          self.drawCircle[k](pos[0], pos[1], rad)
          if self.options.random_colors:
               color(self.randColor[n.sid])
          else:
               color()

          if self.options.show_id:
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
          if self.options.rand_pos:
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
          if self.options.rand_pos:
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


     def setOpts(self, o):
          self.options = o

     def draw(self, g, pos, out):
          self.pos = pos
          
          if self.options.yellow:
               self.edgeColor['h'] = self.setBanana

          self.surfaceCreate(self.options.save_to_png, out)
          
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
          if edges.has_key('msg'):
               for k in edges['msg']:
                    self.drawEdge(k[0], k[1], k[2])
                    if self.options.show_label:
                         self.drawEdgeLabel(k[0], k[1], g.get_edge_data(*k)['label']) 

          # After drawing the lines we draw the nodes themselves
          # Set initial color in a random way (We are tired of the same colors all the time)
          colors = self.colorpick[:]
          randColors = self.options.random_colors
          colorAssign = self.colorAssign
          for n in g.nodes():
               try:
                    self.drawNode(n, 0.005, n.isLeader(), colorAssign[n.sid] )
               except:
                    if randColors:
                         colorAssign[n.sid] = self.getRandColor
                         r = random.randint( 0, 0xFFFFFF )
                         self.randColor[n.sid] = ( (((r>>16)&0xFF)*1.0/255, ((r>>8)&0xFF)*1.0/255, (r&0xFF)*1.0/255 ) )
                    else:
                         colorAssign[n.sid] = colors.pop()
                    self.drawNode(n, 0.005, n.isLeader() , colorAssign[n.sid] )

          if self.options.save_to_png == True:
               self.c.translate (0.1, 0.1) # Changing the current transformation matrix
               self.surface.write_to_png(out) # Output to PNG

