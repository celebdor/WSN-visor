import os,sys,re

class propParser:
     def __init__(self):
          self.pos = dict()

     def parse(self, f):
          pos = self.pos
          f = open(f, 'r')
          pat = re.compile('(.*?) (.*?) (.*)')
          for l in f:
               s = pat.search(l)
               if s:
                    id = int(s.group(1), 0)
                    x = float(s.group(2))
                    y = float(s.group(3))
                    pos[id] = (x,y)

     def normalize(self):
          pos = self.pos
          xM = 0.0
          xm = 100000.0
          yM = 0.0
          ym = 100000.0
          for k in pos.keys():
               if xM < pos[k][0]:
                    xM = pos[k][0]
               if yM < pos[k][1]:
                    yM = pos[k][1]
               if xm > pos[k][0]:
                    xm = pos[k][0]
               if ym > pos[k][1]:
                    ym = pos[k][1]
          dx = xM - xm
          dy = yM - ym
          for k in pos.keys():
               pos[k] = ((pos[k][0]-xm)/dx, (pos[k][1]-ym)/dy)
