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
from optparse import OptionParser
import os,sys,re

class stripParser:
     def __init__(self):
          usage = 'usage: dimi_formatter.py inputFile'
          aparser = OptionParser(usage, version="dimi_formatter-0.1")
          
          (self.options, args) = aparser.parse_args()
          if len(args) == 0:
               aparser.error('Incorrect usage')
               sys.exit(0)
          self.f = open(args[0], 'r')

     def parseMetrics(self):
          f = self.f
          nodeDict = dict()
          
          for l in f:
               #pattern = re.compile('Text..(.?)$')
               pattern = re.compile('.*?(Source )(.*)')
               s = pattern.search(l)
               if s:
                    print s.group(1)+s.group(2)

def main():
     s = stripParser()
     s.parseMetrics()

if __name__ == "__main__":
     sys.exit(main())
