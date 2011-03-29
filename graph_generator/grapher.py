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
from dateutil.parser import *
import sys,re
import matplotlib.pyplot as plt

class stripParser:
    def __init__(self):
        usage = 'usage: dimi_formatter.py inputFile'
        aparser = OptionParser(usage, version="tool-0.1")
        aparser.add_option('-r', '--delivery_rate', action='store_true', default=False, dest='deliveryRate', help='Makes metrics of sent and received instead of sizes.')
        aparser.add_option('-e', '--percentage', action='store_true', default=False, dest='percent', help='Shows the delivery rate in percentage.')
        aparser.add_option('-p', '--plot', action='store_true', default=False, dest='plot', help='Plots the data using matplotlib.')
        self.timeSet = False

        (self.options, args) = aparser.parse_args()
        if len(args) == 0:
            aparser.error('Incorrect usage')
            sys.exit(0)
        self.f = open(args[0], 'r')
        self.hwys = list()
        self.cluster = cluster()

    def hwys_avg(self):
        avg = 0
        for h in self.hwys:
            avg += h.h
        if len(self.hwys) == 0:
            return 0
        else:
            return avg*1.0/len(self.hwys)

    def parse(self):
        if self.options.deliveryRate:
            self.parseDR()
        else:
            self.parseMetrics()

    def parseDR(self):
        f = self.f
        t = self.timeSet
        delta = 0
        sent = received = 0
        p = self.options.plot
        e = self.options.percent
        pattern = re.compile('.*?Text \[(.*?)\].*?Time\[(.*?)\]')
        patternSent = re.compile('.*?SENT; (.*?); (.*?)\]')
        patternReceived = re.compile('.*?RECV; (.*?); (.*?)\]')
        patternShut = re.compile('.*?(0x.*?)\].*HWY_SHUT\]')
        if p:
            time = list()
            if e:
                perList = list()
            else:
                sentList = list()
                recvList = list()
        else:
            if e:
                print 'Time Delivery_rate'
            else:
                print 'Time Sent Received'

        for l in f:
            s = pattern.search(l)
            if s:
                s2 = patternSent.search(l)
                s3 = patternReceived.search(l)
                s4 = patternShut.search(l)
                if not t:
                    t = True
                    zero = parse(s.group(2))
                    if not s2 and not s3 and not s4:
                        if p:
                            time.append(0.0)
                            if e:
                                perList.append(0)
                            else:
                                sentList.append(0)
                                recvList.append(0)
                        else:
                            if e:
                                print '0.0 0.0'
                            else:
                                print '0.0 0 0'

                nt = parse(s.group(2))
                delta = nt-zero

                if s2:
                    sent += 1
                elif s3:
                    received += 1
                elif s4:
                    if p:
                        plt.axvline(x=delta.seconds+delta.microseconds*1.0/1000000)
                if p:
                    time.append(delta.seconds+delta.microseconds*1.0/1000000)
                    if e:
                        if sent == 0:
                            perList.append(0.0)
                        else:
                            perList.append(received*1.0/sent)
                    else:
                        sentList.append(sent)
                        recvList.append(received)
                else:
                    if e:
                        print delta.seconds.__str__()+'.'+delta.microseconds.__str__()[:-3], received*1.0/sent
                    else:
                        print delta.seconds.__str__()+'.'+delta.microseconds.__str__()[:-3], sent, received
        if p:
            if e:
                plt.plot(time, perList, 'r-', label = 'sent')
                plt.ylabel( 'Percentage of delivered messages' )
            else:
                plt.plot(time, sentList, 'r-', label = 'sent')
                plt.plot(time, recvList, 'b-', label = 'received')
                plt.ylabel( 'Amount of messages' )
            plt.xlabel( 'Time in seconds' )
            plt.legend()
            plt.grid(True)
            plt.show()
        else:
            print delta.seconds.__str__()+'.'+delta.microseconds.__str__()[:-3], sent, received

    def parseMetrics(self):
        f = self.f
        t = self.timeSet
        delta = 0
        p = self.options.plot
        pattern = re.compile('.*?Text \[(.*?)\].*?Time\[(.*?)\]')
        patternAdd = re.compile('.*?HWY_ADDED; (.*?); (.*?); (.*?); (.*?); (.*?)\]')
        patternDel = re.compile('.*?HWY_DEL; (.*?); (.*?); (.*?); (.*?)\]')
        patternClus = re.compile('.*?(0x.*?)\].*?HWY_CLUS; (.*?); (.*?)\]')
        patternShut = re.compile('.*?(0x.*?)\].*HWY_SHUT\]')
        if p:
            time = list()
            clusList = list()
            avgCList = list()
            hwysList = list()
            avgHList = list()
        else:
            print 'Time clusters avg_cluster_size highways avg_highways_size'

        for l in f:
            s = pattern.search(l)
            if s:
                s2 = patternAdd.search(l)
                s3 = patternDel.search(l)
                s4 = patternClus.search(l)
                s5 = patternShut.search(l)
                if not t:
                    t = True
                    zero = parse(s.group(2))
                    if not s2 and not s3:
                        if p:
                            time.append(0.0)
                            clusList.append(0)
                            avgCList.append(0)
                            hwysList.append(0)
                            avgHList.append(0)
                        else:
                            print '0.0 0 0.0 0 0.0'

                if s2:
                    nt = parse(s.group(2))
                    delta = nt-zero
                    h = highway(s2.group(1), s2.group(2), s2.group(3), s2.group(4), s2.group(5) )
                    if not h in self.hwys:
                        self.hwys.append(h)
                elif s3:
                    nt = parse(s.group(2))
                    delta = nt-zero
                    h = highway(s3.group(1), s3.group(2), s3.group(3), s3.group(4), str(0) )
                    if h in self.hwys:
                        self.hwys.remove(h)
                elif s4:
                    nt = parse(s.group(2))
                    delta = nt-zero
                    self.cluster.update(s4.group(1), s4.group(2) )
                elif s5:
                    nt = parse(s.group(2))
                    delta = nt-zero
                    self.cluster.remove(s5.group(1))
                    l = list()
                    for i in range(len(self.hwys)):
                        if not self.hwys[i].contains(int(s5.group(1), 0)):
                            l.append(self.hwys[i])
                    self.hwys = l
                    if p:
                        plt.axvline(x=delta.seconds+delta.microseconds*1.0/1000000)
                else:
                    end = parse(s.group(2))
                    delta = end-zero
                if p:
                    time.append(delta.seconds+delta.microseconds*1.0/1000000)
                    clusList.append(len(self.cluster))
                    avgCList.append(self.cluster.avg())
                    hwysList.append(len(self.hwys))
                    avgHList.append(self.hwys_avg())
                else:
                    print delta.seconds.__str__()+'.'+delta.microseconds.__str__()[:-3], len(self.cluster), self.cluster.avg(), len(self.hwys), self.hwys_avg()
        if p:
            plt.plot(time, clusList, 'r-', label = 'clusters', linewidth=2)
            plt.plot(time, avgCList, 'm-', label = 'Avg. cluster size', linewidth=2)
            plt.plot(time, hwysList, 'b-', label = 'highways', linewidth=2)
            plt.plot(time, avgHList, 'g-', label = 'Avg. highway size', linewidth=2)
            plt.ylabel( 'Amount' )
            plt.xlabel( 'Time in seconds' )
            plt.legend()
            plt.grid(True)
            plt.show()
        else:
            print delta.seconds.__str__()+'.'+delta.microseconds.__str__()[:-3], len(self.cluster), self.cluster.avg(), len(self.hwys), self.hwys_avg()

class highway:
    def __init__(self, ps, pt, cs, ct, ho):
        self.h = int(ho, 0)
        if int(cs, 0) < int(ct, 0):
            self.cs = int(cs, 0)
            self.ct = int(ct, 0)
            self.ps = int(ps, 0)
            self.pt = int(pt , 0)
        else:
            self.cs = int(ct, 0)
            self.ct = int(cs, 0)
            self.ps = int(pt, 0)
            self.pt = int(ps, 0)

    def contains(self, a):
        return a == self.cs or a ==self.ct or a == self.ps or a == self.pt

    def __eq__(self, b):
        if (self.ps != 0 and self.pt != 0) and (b.ps != 0 and b.pt != 0):
            return self.ps == b.ps and self.pt == b.pt and self.cs == b.cs and self.ct == b.ct
        else:
            return self.cs == b.cs and self.ct == b.ct

    def __str__(self):
        return 'Ps: '+hex(self.ps)+' Pt: '+hex(self.pt)+' Cs: '+hex(self.cs)+' Ct: '+hex(self.ct)+' hops: '+str(self.h)

class cluster:
    def __init__(self):
        self.d = dict();

    def update(self, id, sid):
        self.d[id] = id == sid

    def remove(self, id):
        del self.d[id]

    def avg(self):
        if len(self) == 0:
            return 0
        else:
            return len(self.d)/len(self)

    def __len__(self):
        r = 0
        d = self.d
        for k in d.keys():
            if d[k]:
                r += 1
        return r


def main():
    s = stripParser()
    s.parse()

if __name__ == "__main__":
    sys.exit(main())
