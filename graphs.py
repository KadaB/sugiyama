#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sugiyama import *

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import cairo


# Data structure for Graph
#   nodes = { 'A': {'in': [], 'out': []}, 'B': {..}, ..}
#   'A': {..}, 'A' is key/lable/id of node {..} is node object
#       in: parents of nodes or nodes having an edge to this node (contain key of nodes)
#       out: child nodes or edges to other nodes from this node (contain key of nodes)

# For drawing:
#   level = [ [ [ 'A', 'B', 'C' ] ], .., [ 'X', 'Y', 'Z'] ]     Grid of nodes
#       =>
#   nodes = { 'A': {'in': [], 'out': [], 'pos': (x, y)}, 'B': {}, ..}
class GraphDrawer(Gtk.Window):
    def __init__(self, res, Graph, levels):
        super(GraphDrawer, self).__init__()

        # setup GTK
        darea = Gtk.DrawingArea()
        darea.connect("draw", self.on_draw)
        self.add(darea)

        self.set_title("GraphDrawer")
        self.resize(*res)

        self.connect("delete-event", Gtk.main_quit)

        self.show_all()

        # setup graph drawing context
        self.level = levels
        H = len(levels)
        self.nodeSize = (1. / H)*0.4    # diameter
        self.lineWidth = self.nodeSize * 0.07
        self.fontSize = self.nodeSize * 0.8
        self.arrowDegrees = math.pi / 14.

        self.graph = Graph


    def arrowEdges(self, start, end):
        # calculate arrow head by taking a certain lenght for the arrow head and 
        # rotate the angle of the arrow for one side
        # and rotate the arrow line by the mirror angle for the other side.
        start_x, start_y = start

        end_x, end_y = end
        angle = math.atan2 (end_y - start_y, end_x - start_x) + math.pi;

        arrowlength = self.nodeSize * 0.7

        degrees = self.arrowDegrees
        x1 = end_x + arrowlength * math.cos(angle - degrees);
        y1 = end_y + arrowlength * math.sin(angle - degrees);
        x2 = end_x + arrowlength * math.cos(angle + degrees);
        y2 = end_y + arrowlength * math.sin(angle + degrees);
        return x1, y1, x2, y2

    def drawArrow(self, pos0, pos1):
        cr = self.cr
        setback = self.nodeSize * 0.5 # diameter /2 if from center to outside of circle

        x, y = pos0
        x2, y2 = pos1
        a = x2 - x
        b = y2 - y

        # rearrange vector, by decreasing vector length by setback
        l = math.sqrt(a*a + b*b)
        a /= l
        b /= l
        l -= setback
        x2 = x + (a * l)
        y2 = y + (b * l)

        cr.save()
        cr.set_line_width(self.lineWidth)
        cr.move_to(x, y)
        cr.line_to(x2, y2)
        cr.stroke()

        ax, ay, bx, by = self.arrowEdges((x, y), (x2, y2))
        cr.move_to(bx, by)
        cr.line_to(x2, y2)
        cr.line_to(ax, ay)
        cr.close_path()
        cr.fill()
        cr.restore()

    def drawNode(self, pos, txt):
        size = self.nodeSize * .5 # radus = diameter /2.
        cr = self.cr
        x, y = pos
        cr.save()

        cr.set_line_width(self.lineWidth)

        cr.arc(x, y, size, 0, 2. * math.pi)

        cr.set_source_rgb (0.4, 0.6, 0.8) # Solid color
        cr.fill_preserve()
        cr.set_source_rgb (0, 0, 0) # Solid color
        cr.stroke()

        cr.set_font_size(self.fontSize)

        xb, yb, tw, th, xd, yd = cr.text_extents(txt)
        cr.move_to(x - xb - (tw/2.0), y + (th/2.0)) # y + yd + (th / 2.0)
        cr.show_text(txt)
        cr.stroke()

        cr.restore()

    # input:
    def drawSugiyamaGraph(self):
        level = self.level
        cr = self.cr
        nodes = self.graph
    #       nodes = { 'A': {'in': [], 'out': [] .. } ->  { 'A': {'in': [], 'out': [], 'pos': (x, y)}, .. }
        convertGridToCart(nodes, level)

    #        nodes = { 'A': [ [], [], [] ], 'B': [ [], [], [] ], 'C': [ [], [], [] ] }
    #        nodes['A'] = [[p0, .., p_n], [c0, .., c_n], (x, y)]
    #                      nodes['A'][0]  nodes['A'][1]  nodes['A'][2]
    #                          in               out        pos
        
        # draw edges first
        for n in nodes:                 # n is number... should be label.. or string
            x, y = nodes[n]['pos']  # get position
            for c in nodes[n]['out']:   # for each child
                x2, y2 = lc = nodes[c]['pos']   # get position for child (in different notation)

                if nodes[c].get('between') == None:  # child index positive  (zwischenknoten
                    self.drawArrow((x, y), lc) 
                else:
                    # draw line to Kasten
                    cr.save()
                    cr.set_line_width(self.lineWidth)
                    cr.move_to(x, y)
                    cr.line_to(x2, y2)
                    cr.stroke()
                    cr.restore()

        # draw nodes
        for n in nodes:
            x, y = nodes[n]['pos']

            if nodes[n].get('between') == None:  # child index positive  (zwischenknoten
                self.drawNode((x, y), str(n))
            else:
                # draw Kasten
                cr.save()
                cr.set_line_width(self.lineWidth)
                rectSize = self.nodeSize /3.
                cr.rectangle(x - rectSize/2, y - rectSize/2, rectSize, rectSize);
                cr.set_source_rgb (1, 1, 1);
                cr.fill_preserve();
                cr.set_source_rgb (0, 0, 0);
                cr.stroke();
                cr.restore()

    def on_draw(self, wid, cr):

        self.cr = cr
        w, h = self.get_size() 

        ratio = float(w) / float(h)

        if ratio > 1.0:
            scale = (w / ratio, h)      # w is bigger... don't scale full w...
            trans = ((ratio - 1.) * .5, 0)  # add a padding (in [0, 1.] coordinate space) 
        elif ratio < 1.0:
            scale = (w, h * ratio)
            trans = (0, (1. - ratio) * .5)  # add a padding (in [0, 1.] coordinate space) 
        else:
            scale = (w, h)
            trans = (0, 0)

        cr.scale(*scale);
        cr.translate(*trans);   # setup coordinate system

        self.drawSugiyamaGraph()


# input:
#   nodes = { 'A': [[], [], []] }
#   levelGrid = [ [ [ 'A', 'B', 'C' ] ], .., [ 'X', 'Y', 'Z'] ]     
#           'List of lists' or Grid of nodes, containing node keys(of dict)
def convertGridToCart(G, level):
    # get each level max width and overall max width
    maxW = max([len(l) for l in level])  #maxW = len( max(level, key = lambda l: len(l)) )

    xstep = 1. / maxW # abstand zwischen den spalten

    ystep = 1. / len(level)

    # get coord in datastructure
    y = ystep / 2.
    for l in level: # for each level l in level
        x = xstep/2. +  (maxW - len(l)) / (maxW*2.)  # start pos and centering + padding and centering

        for n in l: # for each node key in l
            G[n]['pos'] = (x , y)       # levels in grid coordinates
            x += xstep

        y += ystep


if __name__ == "__main__":    

    #E = [ ('A', 'B'), ('A', 'E'), ('B', 'C'), ('E', 'B'), ('C' 'E'), ('C', 'D'), ('D', 'C'), ('A', 'C')]
    #E = [ ('1', '2'), ('1', '4'), ('1','6'), ('1', '3'), ('3', '4'), ('4', '5'), ('5', '2'), ('5', '6')]
    E = [(1, 3), (1, 4), (2, 6), (3, 2), (3, 7), (3, 8), (4, 5), (4, 6), (4, 8), (4, 9), (6, 10), (7, 10), (7, 11), (8, 7), (9, 11), (10, 12), (11, 12)]
    G = graphFromEdges(E)
    G, L = sugiyama(G)

    print L

    convertGridToCart(G, L)
    print G

    app = GraphDrawer((600, 600), G, L)
    Gtk.main()

