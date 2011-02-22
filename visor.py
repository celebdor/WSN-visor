#!/usr/bin/env python

from optparse import OptionParser
import sys, math, re, random
import networkx as nx
from dateutil.parser import *
from display import display
from prop import propParser

class wsnVisor:
     def __init__(self):
          usage = 'usage: visor.py [options] inputFile'
          aparser = OptionParser(usage, version="visor 0.9.6")
          aparser.add_option('-s', '--show_id', action='store_true', default=False, dest='show_id', help='displays the nodes with their id.')
          aparser.add_option('-l', '--show_label', action='store_true', default=False, dest='show_label', help='displays the messages with their label.')
          aparser.add_option('-b', '--bigger_leaders', action='store_true', default=False, dest='bigger_leaders', help='displays the cluster leaders in a bigger size.')
          aparser.add_option('-y', '--yellow_highway', action='store_true', default=False, dest='yellow', help='changes the default green color of the highways to yellow.')
          aparser.add_option('-n', '--random_position', action='store_true', default=False, dest='rand_pos', help='Generates a random positioned graph.')
          aparser.add_option('-r', '--random_colors', action='store_true', default=False, dest='random_colors', help='displays the cluster picking the colors randomly.')
          aparser.add_option('-o', '--output', default='example.png', dest='outfile', help='defines the name of the output picture.')
          aparser.add_option('-f', '--prop_file', default='luebeck_fronts.prop', dest='prop', help='defines the file with testbed properties.')
          aparser.add_option('-p', '--png', action='store_true', default='false', dest='save_to_png', help='saves the file in png format, if not set in svg.')
          aparser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose')
          
          (self.options, args) = aparser.parse_args()
          if len(args) != 1:
               aparser.error('incorrect usage')
               sys.exit(0)
          self.f = open(args[0], 'r')
          self.graph = nx.MultiGraph()
          self.counter = 0
          if not self.options.rand_pos:
               p = propParser()
               p.parse(self.options.prop)
               p.normalize()
               self.pos = p.pos

     def cleanEdges(self, kind):
          g = self.graph
          for e in g.edges(g.nodes(), keys=True):
              if e[2] == kind:
                   g.remove_edge(e[0], e[1], e[2]) 

     def clusterEdges(self):
          g = self.graph
          for n in g.node:
               aux = wsnNode( n.parent, n.sid, n.sid)
               if not n.isLeader() and g.has_node(aux):
                    t = g.nodes()[g.nodes().index(aux)]
                    g.add_edge(n, t, key = 'cluster') 

     def highwayEdges(self, n, pS, pT, cS, cT):
          g = self.graph
          if not n.isLeader():
               aux = wsnNode( n.parent, n.sid, n.sid)
               if g.has_node(aux):
                    p = g.nodes()[g.nodes().index(aux)]
                    g.add_edge(n, p, key = 'highway', ps = pS, pt = pT, ss = cS, ts = cT)
                    if p.parent != n.id:
                         self.highwayEdges(p, pS, pT, cS, cT)

     def parseAndDraw(self):
          t = False
          pattern = re.compile('.*?:(0x.*?)\].*?Text \[(.*?)\].*?Time\[(.*?)\]')
          patternDel = re.compile('HWY_DEL; (.*?); (.*?); (.*?); (.*)')
          patternAdd = re.compile('HWY_ADDED; (.*?); (.*?); (.*?); (.*?)(;|$)')
          patternClus = re.compile('HWY_CLUS; (.*?); (.*)')
          patternMsg = re.compile('HWY_MSG; (.*?); (.*?); (.*?)(,|;|$)' )
          patternShut = re.compile('HWY_SHUT')
          p = dict()
          g = self.graph
          d = display()
          d.setOpts(self.options)
          for l in self.f:
               s = pattern.search(l)
               if s:
                    if s.group(1) == 0x2e1:
                         print l
                    self.cleanEdges('msg')
                    if not t:
                         t = True
                         zero = parse(s.group(3))
                    else:
                         nt = parse(s.group(3))
                         delta = nt-zero
                         sD = patternDel.search(s.group(2))
                         sC = patternClus.search(s.group(2))
                         sM = patternMsg.search(s.group(2))
                         sA = patternAdd.search(s.group(2))
                         sS = patternShut.search(s.group(2))
                         if sC:
                              n = wsnNode(int(s.group(1), 0), int(sC.group(1), 0), int(sC.group(2), 0) )
                              at = 'sC'+str(n)
                              # Add or update the node accordingly (networkx managed)
                              if g.has_node(n):
                                   g.remove_node(n)
                                   g.add_node(n)
                              else:
                                   g.add_node(n)
                              self.clusterEdges()

                         elif sD: #Iterate through the edges and remove those with the highway in the dictionary
                              at = 'sD'
                              ps = sD.group(1)
                              pt = sD.group(2)
                              ss = sD.group(3)
                              ts = sD.group(4)
                              for e in g.edges(g.nodes(), keys=True):
                                  if e[2] == 'highway':
                                       eD = g.get_edge_data(*e)
                                       if (ps == eD['ps'] and pt == eD['pt'] and ss == eD['ss'] and ts == eD['ts']) or (pt == eD['ps'] and ps == eD['pt'] and ts == eD['ss'] and ss == eD['ts']):
                                            g.remove_edge(*e) 

                         elif sA: #Go to each of the ports and add the edges till the cluster leader with the highway four parts in the dictionary
                              at = 'sA'+'_'+sA.group(1)+':'+sA.group(2)+':'+sA.group(3)+':'+sA.group(4)
                              ps = wsnNode( int(sA.group(1), 0), 0, 0)
                              recalc = False
                              if g.has_node(ps):
                                   pS = g.nodes()[g.nodes().index(ps)]
                              pt = wsnNode( int(sA.group(2), 0), 0, 0)
                              if g.has_node(pt):
                                   pT = g.nodes()[g.nodes().index(pt)]
                              ss = wsnNode( int(sA.group(3), 0), 0, 0)
                              if g.has_node(ps):
                                   sS = g.nodes()[g.nodes().index(ss)]
                              st = wsnNode( int(sA.group(4), 0), 0, 0)
                              if g.has_node(pt):
                                   sT = g.nodes()[g.nodes().index(st)]
                              if not sS.isLeader():
                                   sS.sid = sS.id
                                   sS.parent = sS.id
                                   self.clusterEdges()
                                   recalc = True
                              if not sT.isLeader():
                                   sT.sid = sT.id
                                   sT.parent = sT.id
                                   recalc = True
                              if recalc:
                                   self.clusterEdges()
                              self.highwayEdges(pS, sA.group(1), sA.group(2), sA.group(3), sA.group(4))
                              self.highwayEdges(pT, sA.group(1), sA.group(2), sA.group(3), sA.group(4))
                              g.add_edge(pS, pT, key = 'highway', ps = sA.group(1), pt = sA.group(2), ss = sA.group(3), ts = sA.group(4))

                         elif sM:
                              at = 'sM'
                              # Message displaying
                              mId = sM.group(1)
                              o = wsnNode( int(sM.group(3), 0 ), 0, 0 )
                              t = wsnNode( int(sM.group(2), 0 ), 0, 0 )
                              if  mId == 'CAND':
                                   g.add_edge( o, t, key = 'msg', label = mId  )
                              if  mId == 'REQ':
                                   g.add_edge( o, t, key = 'msg', label = mId  )
                              if  mId == 'PACK':
                                   g.add_edge( o, t, key = 'msg', label = mId  )
                              if  mId == 'PNACK':
                                   g.add_edge( o, t, key = 'msg', label = mId,  )
                              if  mId == 'SEND':
                                   g.add_edge( o, t, key = 'msg', label = mId  )
                              if  mId == 'ACK':
                                   g.add_edge( o, t, key = 'msg', label = mId  )
                         elif sS:
                              at = 'sS'
                              o = wsnNode(int(s.group(1), 0, 0))
                              g.remove_node(o)

                         if self.options.rand_pos:
                              if len(p.keys()) == 0:
                                   p = nx.spring_layout(g)
                              else:
                                   p = nx.spring_layout(g, dim=2, pos=p, fixed=p.keys())
                         else:
                              p = self.pos

                         if sC or sA or sM or sS or sD:
                              if self.options.save_to_png:
                                   out = self.options.outfile+'_'+str(self.counter)+'_'+str(delta.seconds)+'_'+str(delta.microseconds)[:-3]+at+'.png'
                              else:
                                   out = self.options.outfile+'_'+str(self.counter)+'_'+str(delta.seconds)+'_'+str(delta.microseconds)[:-3]+at+'.svg'
                              self.counter+=1
                              d.draw(g, p, out)

class wsnNode:
     def __init__(self):
          self.id = 0
          self.sid = 0
          self.parent = 0

     def __init__(self, i, s, p):
          self.id = i
          self.sid = s
          self.parent = p

     def __hash__(self):
          return self.id;

     def __eq__(self, b):
          return self.id == b.id

     def isLeader(self):
          return self.id == self.sid

     def __cmp__(self, b):
          return cmp(self.id, b.id)

     def __str__(self):
          return hex(self.id)+':'+hex(self.sid)+':'+hex(self.parent)

def main():
     v = wsnVisor()
     v.parseAndDraw()

if __name__ == "__main__":
     sys.exit(main())
