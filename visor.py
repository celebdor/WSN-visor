#!/usr/bin/env python

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
import sys, re
import networkx as nx
from dateutil.parser import parse
from display import Display
from prop import propParser
from functools import partial


class WSNVisor:
    """ wsnVisor is a module that takes a testbed output file, turns each entry
    into a networkx representation and generates a picture of it through the 
    display module."""
    def __init__(self):
        """Parses options from the console and creates a wsnVisor object."""
        usage = 'usage: visor.py [options] inputFile'
        aparser = OptionParser(usage, version="visor 0.9.6")
        aparser.add_option('-s', '--show_id', action='store_true',
                           default=False, dest='show_id',
                           help='Displays the nodes with their id.')
        aparser.add_option('-l', '--show_label', action='store_true',
                           default=False, dest='show_label',
                           help='Displays the messages with their label.')
        aparser.add_option('-b', '--bigger_leaders', action='store_true',
                           default=False, dest='bigger_leaders',
                           help='Displays the cluster leaders bigger.')
        aparser.add_option('-y', '--yellow_highway', action='store_true',
                           default=False, dest='yellow',
                           help='Green instead of yellow for highway edges.')
        aparser.add_option('-n', '--random_position', action='store_true',
                           default=False, dest='rand_pos',
                           help='Generates a random positioned graph.')
        aparser.add_option('-r', '--random_colors', action='store_true',
                           default=False, dest='random_colors',
                           help='Displays the cluster with random colors.')
        aparser.add_option('-o', '--output', default='example.png',
                           dest='outfile',
                           help='Defines the name of the output picture.')
        aparser.add_option('-f', '--prop_file', default='luebeck_fronts.prop',
                           dest='prop',
                           help='Defines the file with testbed properties.')
        aparser.add_option('-p', '--png', action='store_true', default='false',
                           dest='save_to_png',
                           help='Saves the file in png format.(Default: svg.')
        aparser.add_option('-v', '--verbose', action='store_true',
                           default=False, dest='verbose')

        (self.options, args) = aparser.parse_args()
        if len(args) != 1:
            aparser.error('incorrect usage')
            sys.exit(0)
        self.input_file = open(args[0], 'r')
        self.graph = nx.MultiGraph()
        self.counter = 0
        self.disp = Display()
        self.disp.options = self.options
        self.toint = partial(int, base = 0)
        if not self.options.rand_pos:
            parser = propParser()
            parser.parse(self.options.prop)
            parser.normalize()
            self.pos = parser.pos

    def clean_edges(self, kind):
        """ Removes all the graphs edges that match kind.

        Keyword arguments:
        kind --- A string that defines a kind of edge. """
        graph = self.graph
        for edge in graph.edges(graph.nodes(), keys=True):
            if edge[2] == kind:
                graph.remove_edge(edge[0], edge[1], edge[2])

    def cluster_edges(self):
        """ Adds all the cluster edges to the graph. """
        graph = self.graph
        for node in graph.node:
            aux = WSNNode( node.parent, node.sid, node.sid)
            if not node.is_leader() and graph.has_node(aux):
                target_node = graph.nodes()[graph.nodes().index(aux)]
                graph.add_edge(node, target_node, key = 'cluster')

    def highway_edges(self, node, port_s, port_t, cluster_s, cluster_t):
        """ Recursively adds all the edges from port to leader of a certain
        highway.

        Keyword arguments:
        node --- The node from which to start adding edges.
        port_s --- The port source id.
        port_t --- The port target id.
        cluster_s --- The cluster source id.
        cluster_t --- The cluster target id. """
        graph = self.graph
        if not node.is_leader():
            aux = WSNNode(node.parent, node.sid, node.sid)
            if graph.has_node(aux):
                target_node = graph.nodes()[graph.nodes().index(aux)]
                graph.add_edge(node, target_node, key = 'highway', ps = port_s,
                               pt = port_t, ss = cluster_s, ts = cluster_t)
                if target_node.parent != node.id:
                    self.highway_edges(target_node, port_s, port_t, cluster_s,
                                       cluster_t)

    def __process_clus_ev(self, node_id, clus_ev):
        """Adds or update the node accordingly (networkx managed)"""
        cluster_id, parent_id = (self.toint(x) for x in clus_ev.group(1, 2))
        node = WSNNode(self.toint(node_id), cluster_id, parent_id)
        if self.graph.has_node(node):
            self.graph.remove_node(node)
            self.graph.add_node(node)
        else:
            self.graph.add_node(node)
        self.cluster_edges()
        return 'clus_ev'+str(node)

    def __process_hwy_del_ev(self, hwy_del_ev):
        """Iterate through the edges and remove those with the highway in the
        dictionary"""
        port_s, port_t, clus_s, clus_t = hwy_del_ev.group(1, 2, 3, 4)
        graph = self.graph
        for edge in graph.edges(graph.nodes(), keys=True):
            if edge[2] == 'highway':
                ed_data = graph.get_edge_data(*edge)
                if ( port_s == ed_data['ps'] and port_t == ed_data['pt']
                     and clus_s == ed_data['ss'] and clus_t == ed_data['ts']) \
                    or \
                   ( port_t == ed_data['ps'] and port_s == ed_data['pt']
                     and clus_t == ed_data['ss'] and clus_s == ed_data['ts']
                   ):
                    self.graph.remove_edge(*edge)
        return 'hwy_del_ev'

    def __process_add_ev(self, add_ev):
        """Go to each of the ports and add the edges till the cluster leader
        with the highway four parts in the dictionary"""
        port_s, port_t, clus_s, clus_t = add_ev.group(1, 2, 3, 4)
        search = WSNNode(self.toint(port_s), 0, 0)
        graph = self.graph
        if graph.has_node(search):
            nport_s = graph.nodes()[graph.nodes().index(search)]
        else:
            return None
        search = WSNNode(self.toint(port_t), 0, 0)
        if graph.has_node(search):
            nport_t = graph.nodes()[graph.nodes().index(search)]
        else:
            return None
        search = WSNNode(self.toint(clus_s), 0, 0)
        if graph.has_node(search):
            nclus_s = graph.nodes()[graph.nodes().index(search)]
        else:
            return None
        search = WSNNode(self.toint(clus_t), 0, 0)
        if graph.has_node(search):
            nclus_t = graph.nodes()[graph.nodes().index(search)]
        else:
            return None

        if not nclus_s.is_leader():
            nclus_s.sid, nclus_s.parent = clus_s, clus_s
            self.cluster_edges()
        if not nclus_t.is_leader():
            nclus_t.sid, nclus_t.parent = clus_t, clus_t
            self.cluster_edges()
        self.highway_edges(nport_s, port_s, port_t, clus_s, clus_t)
        self.highway_edges(nport_t, port_s, port_t, clus_s, clus_t)
        graph.add_edge(nport_s, nport_t, key = 'highway', ps = port_s,
                       pt = port_t, ss = clus_s, ts = clus_t)
        return 'add_ev'+'_'+port_s+':'+port_t+':'+clus_s+':'+clus_t

    def __process_msg_ev(self, msg_ev):
        """Adds the message edge to the graph."""
        msg_id, target_id, source_id = msg_ev.group(1, 2, 3)
        self.graph.add_edge(WSNNode(self.toint(source_id), 0, 0),
                            WSNNode(self.toint(target_id), 0, 0), key = 'msg',
                            label = msg_id)
        return 'msg_ev'

    def __update_topology(self, pos):
        """Updates the graph topology for drawing."""
        if self.options.rand_pos:
            if len(pos.keys()) == 0:
                pos = nx.spring_layout(self.graph)
            else:
                pos = nx.spring_layout(self.graph, dim=2, pos=pos,
                                       fixed=pos.keys())
        else:
            pos = self.pos
        return pos

    def __draw(self, pos, delta, filename):
        """Uses the display to draw the frame."""
        if self.options.save_to_png:
            out = self.options.outfile + '_' + str(self.counter) + \
            '_' + str(delta.seconds) + '_' + \
            str(delta.microseconds)[:-3]+filename+'.png'
        else:
            out = self.options.outfile + '_' + str(self.counter) + \
            '_' + str(delta.seconds) + '_' + \
            str(delta.microseconds)[:-3]+filename+'.svg'
        self.counter += 1
        pos = self.__update_topology(pos if pos else {})
        self.disp.draw(self.graph, pos, out)
        return pos
    
    def parse_and_draw(self):
        """ Parses the testbed output file and makes a drawing per entry. """
        time_started = False
        pattern = re.compile('.*?:(0x.*?)\].*?Text \[(.*?)\].*?Time\[(.*?)\]')
        pos = None
        events = filter(lambda x: x is not None,
                       (pattern.search(line) for line in self.input_file))
        for event in events:
            self.clean_edges('msg')

            node_id, ev_text, time = event.group(1, 2, 3)
            if not time_started:
                time_started = True
                zero = parse(time)
            delta = parse(time)-zero

            hwy_ev = re.compile('HWY_CLUS; (.*?); (.*)').search(ev_text)
            if hwy_ev:
                filename = self.__process_clus_ev(node_id, hwy_ev)
                pos = self.__draw(pos, delta, filename)
                continue

            hwy_ev = re.compile('HWY_DEL; (.*?); (.*?); (.*?); (.*)').\
                    search(ev_text)
            if hwy_ev:
                filename = self.__process_hwy_del_ev(hwy_ev)
                pos = self.__draw(pos, delta, filename)
                continue

            hwy_ev = re.compile('HWY_ADDED; (.*?); (.*?); (.*?); (.*?)(;|$)').\
                    search(ev_text)
            if hwy_ev:
                filename = self.__process_add_ev(hwy_ev)
                if filename is None:
                    continue
                pos = self.__draw(pos, delta, filename)
                continue

            hwy_ev = re.compile('HWY_MSG; (.*?); (.*?); (.*?)(,|;|$)' ).\
                    search(ev_text)
            if hwy_ev:
                filename = self.__process_msg_ev(hwy_ev)
                pos = self.__draw(pos, delta, filename)
                continue

            hwy_ev = re.compile('HWY_SHUT').search(ev_text)
            if hwy_ev:
                self.graph.remove_node(WSNNode(self.toint(node_id), 0, 0))
                filename = 'shutdown_ev'
                pos = self.__draw(pos, delta, filename)
                continue

        self.input_file.close()

class WSNNode: #pylint: disable-msg=R0903 
    """This module models a wireless sensor netowork node with its id,
    cluster id and parent node."""
    def __init__(self, node_id, cluster_id, parent_id):
        """ Initializes a node.

        Keyword arguments:
        i --- id of the WSNNode.
        s --- cluster id of the WSNNode.
        p --- id of the wsn_node's parent. """
        self.id = node_id
        self.sid = cluster_id
        self.parent = parent_id

    def __hash__(self):
        """Returns the hash value of a wsn_node."""
        return self.id

    def __eq__(self, rhs):
        """Returns if two WSNNodes are equal or differ."""
        return self.id == rhs.id

    def is_leader(self):
        """Returns true when the node is a cluster leader."""
        return self.id == self.sid

    def __cmp__(self, rhs):
        """ Compares two WSNNodes ids. """
        return cmp(self.id, rhs.id)

    def __str__(self):
        """Returns a wsn_nodes representation with the following format:
        id(in Hex):cluster_id(in Hex):parent_id(in Hex)
        For example:
        0xaa:0xab:0x3c"""
        return hex(self.id)+':'+hex(self.sid)+':'+hex(self.parent)

def main():
    """Main function for running the visor as a script"""
    visor = WSNVisor()
    visor.parse_and_draw()

if __name__ == "__main__":
    sys.exit(main())
