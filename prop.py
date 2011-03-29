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
import re

class propParser:
    """The propParser module parses a prop file (csv) that contains nodeId x y and produces a dictionary indexed by the node id. """
    def __init__(self):
        """ Initializes the propParser with an empty dictionary. """
        self.pos = dict()

    def parse(self, f):
        """ Parses a file into the dictionary.

        Keyword arguments:
        f --- a file object from which to read the content. """
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
        f.close()

    def normalize(self):
        """ Normalizes all the coordinates to 0..1 reals. """
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
