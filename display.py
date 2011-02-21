#!/usr/bin/env python

from optparse import OptionParser
import sys, math, re, random
import cairo

pi = math.pi
VERBOSE=False
YELLOW_HIGHWAYS=False

class display:
	def __init__(self):
		#Default topology sizes
		self.width = 1024
		self.height = 1024

		self.drawCircle = {'True': self.leaderCircle, 'False' : self.standardCircle}
		self.edgeColor = {'msg': self.setBlueViolet, 'highway': self.setAppleGreen, 'cluster': self.setWhite}
		self.edgeWidth = {'msg': self.setThin, 'highway': self.setThick, 'cluster': self.setMedium}
		self.colorpick = [self.setAirForceBlue, self.setAlizarin, self.setAmber, self.setAppleGreen, self.setArmyGreen, self.setAsparagus, self.setBanana, self.setBlueViolet, self.setBurgundy, self.setBubblegum, self.setByzantine, self.setCamel, self.setCarrotOrange, self.setInchWorm, self.setOlive]

	def surfaceCreate(self, png):
		if png == True:
			self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
		else:
			self.surface = cairo.SVGSurface(self.parser.options.outfile, self.width, self.height)
		self.c = cairo.Context (self.surface)
		self.c.scale (self.width, self.height) # Normalizing the canvas
		self.drawBg(0, 0, 0)

	def setThin(self):
		self.c.set_line_width(0.001)

	def setThick(self):
		self.c.set_line_width(0.005)

	def setMedium(self):
		self.c.set_line_width(0.0025)

	def setAirForceBlue(self):
		self.c.set_source_rgb(0.36, 0.54, 0.66)

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
		c.show_text(str(id))
		c.stroke()

	#Empty circle for leaders (Sepia Color)
	def leaderCircle(self, x, y, rad):
		c = self.c
		c.set_source_rgb(0.44, 0.26, 0.08)
		self.setCircleWidth()
		c.arc(x, y, rad/2.0, 0, 2*pi)
		c.stroke()
		if VERBOSE:
			print 'Leader'

	#Empty circle for regular ports (White)
	def standardCircle(self, x, y, rad):
		c = self.c
		c.set_source_rgb(1, 1, 1)
		self.setCircleWidth()
		c.arc(x, y, rad/2.0, 0, 2*pi)
		c.stroke()
		if VERBOSE:
			print 'Standard'

	def drawNode(self, n, rad, k, color, show, bigger):
		if self.options.bigger_leaders and k:
			rad*=3
		self.drawCircle[k](self.pos[0], self.pos[1], rad)
		color()
		if self.options.show_id:
			self.drawNodeId(x, y, rad, id)

		#Filling circle
		c = self.c
		c.set_line_width(0.003)
		c.arc(self.pos[n][0], self.pos[n][1], rad/1.2, 0, 2*pi)
		c.fill()

	def drawBg(self, r, g, b):
		c = self.c
		c.set_source_rgb(r, g, b)
		c.rectangle (0, 0, self.width, self.height) # Rectangle(x0, y0, x1, y1)
		c.fill ()

	def drawEdge(self, o, t, k):
		c = self.c
		self.edgeColor[k]()
		self.edgeWidth[k]()
		c.move_to(self.pos[o][0], self.pos[o][1])
		c.line_to(self.pos[t][0], self.pos[t][1])
		c.stroke()

     def setOpts(self, o):
          self.options = o

	def testParseAndDraw(self, g, pos):
          self.pos = pos
		
		if self.options.yellow:
			self.edgeColor['h'] = self.setBanana

		#nodesDict = parser.nodesDict
		#edgesDict = parser.edgesDict
		self.surfaceCreate(self.options.save_to_png)
		
		#After this step draw lines between nodes and parent id in a new iteration
          edges = dict()
		for k in g.edges(keys = True):
               try:
                    e[k[2]].append(k)
               except:
                    e[k[2]] = list()
                    e[k[2]].append(k)

		#First we draw the cluster edges
          for k in edges['cluster']:
               self.drawEdge(k[0], k[1], k[2])
          
		#Then we draw the highways
          for k in edges['highway']:
               self.drawEdge(k[0], k[1], k[2])
               
		#Finally we draw the message edges
          for k in edges['msg']:
               self.drawEdge(k[0], k[1], k[2])


		# After drawing the lines we draw the nodes themselves
		# Set initial color in a random way (We are tired of the same colors all the time)
		colors = self.colorpick[:]
          randColors = self.options.random_colors
		if randColors:
			#random.shuffle(colors)
               del colors[:]
		colorAssign = dict()
          for n in g.nodes():
			try:
                    if randColors:
                         self.drawNode(n, 0.005, g.isLeader(), self.getRandColor() )
                    else:
                         self.drawNode(n, 0.005, g.isLeader(), colorAssign[n.sid] )
			except:
                    if randColors:
                         colorAssign[n.sid] = self.getRandColor()
                         self.randColor[n.sid].append(random.randint( 0, 0xFFFFFF )
                    else:
                         colorAssign[n.sid] = colors.pop()
                         self.drawNode(n, 0.005, g.isLeader() , colorAssign[n.sid] )

		if parser.options.save_to_png == True:
			self.c.translate (0.1, 0.1) # Changing the current transformation matrix
			self.surface.write_to_png(self.parser.options.outfile) # Output to PNG

