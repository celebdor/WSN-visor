#!/usr/bin/env python

from optparse import OptionParser
import sys, math, re, random
import networkx as nx
from dateutil.parser import *
import display

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
          aparser.add_option('-p', '--png', action='store_true', default='false', dest='save_to_png', help='saves the file in png format, if not set in svg.')
          aparser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose')
          
          (self.options, args) = aparser.parse_args()
          if len(args) != 1:
               aparser.error('incorrect usage')
               sys.exit(0)
          self.f = open(args[0], 'r')
          self.graph = nx.MultiGraph()

     def cleanEdges(self, a):
          g = self.graph
          for e in g.edges(g.nodes(), keys=True):
              if e[2] == 'msg':
                   g.remove_edge(e[0], e[1], e[2]) 

     def clusterEdges(self):
          g = self.graph
          for n in g.node:
               aux = wsnNode( n.parent, n.sid, n.sid)
               if g.has_node(aux):
                    t = g.nodes()[g.nodes().index(aux)]
                    g.add_edge(n, t, key = 'cluster') 

     def parseAndDraw(self):
          t = False
          pattern = re.compile('.*?Text \[(.*?)\].*?Time\[(.*?)\]')
          patternEdge = re.compile('.*?(0x.*?)\].*?HWY_EDGE; (.*?); (.*?); (.*?); (.*?); (.*?)\]')
          patternDel = re.compile('.*?HWY_DEL; (.*?); (.*?); (.*?); (.*?)\]')
          patternClus = re.compile('.*?(0x.*?)\].*?HWY_CLUS; (.*?); (.*?)\]')
          patternMsg = re.compile('.*?HWY_MSG; (.*?); (.*?); (.*?)\]' )
          patternShut = re.compile('.*?(0x.*?)\].*HWY_SHUT\]')
          p = dict()
          g = self.graph
          d = display()
          d.setOpts(self.options)
          for l in self.f:
               s = pattern.search(l)
               if s:
                    if not t:
                         t = True
                         zero = parse(s.group(2))
                    else:
                         nt = parse(s.group(2))
                         delta = nt-zero
                         sD = patternDel.search(l)
                         sC = patternClus.search(l)
                         sM = patternMsg.search(l)
                         sE = patternEdge.search(l)
                         sS = patternShut.search(l)
                         if sC:
                              n = wsnNode(int(sC.group(1), 0), int(sC.group(2), 0), int(sC.group(3), 0) )
                              # Add or update the node accordingly (networkx managed)
                              g.add_node(n)
                              self.clusterEdges()

                         elif sD: #Iterate through the edges and remove those with the highway in the dictionary
                              ps = sE.group(1)
                              pt = sE.group(2)
                              ss = sE.group(3)
                              ts = se.group(4)
                              for e in g.edges(g.nodes(), keys=True):
                                  if e[2] == 'highway':
                                       eD = g.get_edge_data(e)
                                       if (ps == eD['ps'] and pt == eD['pt'] and ss == eD['ss'] and ts == eD['ts']) or (pt == eD['ps'] and ps == eD['pt'] and ts == eD['ss'] and ss == eD['ts']):
                                            g.remove_edge(*e) 

                         elif sE: #Add the edge between the two elements with the highway four parts in the dictionary
                              o = wsnNode( int(sE.group(1), 0), 0, 0)
                              t = wsnNode( int(sE.group(2), 0), 0, 0)
                              g.add_edge(o, t, key = 'highway', ps = sE.group(3), pt = sE.group(4), ss = sE.group(5), ts = se.group(6))

                         elif sM:
                              # Message displaying
                              mId = sM.group(1)
                              o = wsnNode( int(sM.group(3), 0 ), 0, 0 )
                              t = wsnNode( int(sM.group(2), 0 ), 0, 0 )
                              if  mId == 'CAND':
                                   g.add_edge( o, t, key = 'msg', label = mId  )
                              if  mId == 'REQ':
                                   G.add_edge( o, t, key = 'msg', label = mId  )
                              if  mId == 'PACK':
                                   g.add_edge( o, t, key = 'msg', label = mId  )
                              if  mId == 'PNACK':
                                   g.add_edge( o, t, key = 'msg', label = mId,  )
                              if  mId == 'SEND':
                                   g.add_edge( o, t, key = 'msg', label = mId  )
                              if  mId == 'ACK':
                                   g.add_edge( o, t, key = 'msg', label = mId  )

                         self.cleanEdges()
                         p = nx.spring_layout(g, dim=2, pos=p, fixed=pos.keys())
                         d.draw(g, pos, self.options.outfile+delta.seconds.__str__()+'_'+delta.microseconds.__str__()[:-3])

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
          return hex(self.id)

def main():
     v = wsnVisor()
     v.parseAndDraw()

if __name__ == "__main__":
     sys.exit(main())
