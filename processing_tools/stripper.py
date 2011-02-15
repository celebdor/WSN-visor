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
