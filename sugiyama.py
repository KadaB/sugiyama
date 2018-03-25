#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import copy
from graphLib import *
import itertools
import random
import string
import math

# 1. Entfernen von Zyklen
# 2. Schichtzuuordnung
# 3. Kreuzungsreduktion
# 4. Koordinatenzuweisung
# 5. Wiederherstellung der Zyklen

# 1. Entfernen von Zyklen, baue Reienfolge mit Anzahl der Rueckwaertskanten minimal.
#   (a) Speicher Quellen und Senken in zwei verschiedene Listen
#   (b) Entferne zunehmends Quellen und fuege sie der Quellenliste hinzu
#   (c) entferne zunehmends Senken und fuege sie der Senkenliste hinzu
#   (d) Waehle den naechsten Kandidaten anhand der Einwaerts- und Auswaertsgrade. rangOut = maxNode( [R_out(v) - R_in(v) for v in G] )
#       (e) entferne v aus G und fuege der Quellenliste hinzu
def cycleAnalysis(G):
    N = copy.deepcopy(G)    # graph will be altered... copy graph
    printGraph(N)

    Sl, Sr = [], []     # Sl, Sr in Sugiyama et. al.


    while N:        # while N not empty

        sources = [ n for n in N if len(N[n]['in']) == 0 ]
        sinks = [ n for n in N if len(N[n]['out']) == 0 ]

        # (b)
        if sources:
            Sl += sources

            for n in sources:
                removeNode(N, n)    # remove all sinks

        # (c)
        elif sinks:
            Sr += sinks

            for n in sinks:
                removeNode(N, n)    # remove all sinks

        # (d)
        elif N:
            o = max(N, key = lambda n: len(N[n]['out']) - len(N[n]['in']) )    # get node with maximum rangOut 
            # (e)
            Sl += [ o ]
            removeNode(N, o)

    return Sl + Sr

# invert cyclic edge
def invertBackEdges(G, S):
    N = copy.deepcopy(G)    # graph will be altered... copy graph
    B = []  # backedges
    for i, n in enumerate(S):

        C = N[n]['out'] # children
        for c in C:
            j = S.index(c)
            if j < i:
                B += [ (n, c) ]
    
    twistEdges(N, B)

    return N


# 2. Weise die Knoten waagerechten Schichten zu
#   (a) Ermittle alle Senken
#   (b) Ordne sie auf einer neuen Schicht an
#   (c) Entferne alle Senken aus dem Graph und 
# takes acyclic Graph
def levelAssignment(G):
    N = copy.deepcopy(G)

    L = []      # levels

    while N:    # while N not empty
        # (a)
        sinks = [ n for n in N if len(N[n]['out']) == 0 ]
    
        # (c)
        L += [ sinks ]      # L = []; L += [ ['A', 'B', 'C'] ] =>  L = [ ['A', 'B', 'C'] ]

        # (b)
        for n in sinks:
            removeNode(N, n)


    return [ x for x in reversed(L) ]

# take (a, b) and if there lies a level between them (which they are not connected over):
#   take a as from node, 
#   create a new node
#     connect that new node to a
#   connect that new node to b
# for multiple levels in between
def solveMidTransition(N, edge, L):
    (a, b) = edge

    # return the levels that lie between the node

    lfrom = N[a]['level']
    lto = N[b]['level']

    if lto < lfrom:
        step = -1
    else:
        step = 1

    removeEdges(N, [ (a, b) ])   # remove original edge

    u = a   # (u, v)
    for i in range(lfrom + step, lto, step):     # for levels between a and b
        v = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))

        N[u]['out'] += [ v ]
        N[v] = {'in': [u], 'out': [], 'level': i, 'between': True }
        L[i] += [ v ]      # add to level
        u = v

    N[v]['out'] += [ b ]     # u is last created node... connect that one to b
    N[b]['in'] += [ u ]     # u is last created node... connect that one to b

    return N, L

def getInBetweenNodes(G, L):
    N = copy.deepcopy(G)

    for i, l in enumerate(L):
        for j in l:
            N[j]['level'] = i       # assign each node a level

    IB = []

    for nLevel, l in enumerate(L):
        for n in l:
            node = N[n]
            for c in node['out']:
                cLevel = N[c]['level']

                dif = math.fabs(cLevel - nLevel);    # if more than two level between 
                if dif > 1:
                    IB += [ (n, c) ]

    for (n, c) in IB:
        solveMidTransition(N, (n, c), L)

    return N, L

def toIndex(A, B):
    for a in A:
        if a in B:
            yield B.index(a)

# Naive Exhaustive, Two Level comparison
# O( N! * E(N) * 2 )
def minCrossing(N, Levels):

    L = [ x for x in Levels ]    # copy the list, just to make sure..

    R = [ Levels[-1] ]

    # compare level_n+1 with level_n.
    # T will be upper level of pair, B will be lower level of pair.
    # [ 1, 2, 3, 4, 5, 6 ] -> [ (5, 6), (4, 5), (3, 4), (2, 3), (1, 2) ]
    # (T, B)_0 = (5, 6), (T, B)_1 = (4, 5), (T, B)_n = (1, 2) ]
    # T will be used to permute and after chosing an optimal permutation will be used as base 
    # for next level (B) cross testing

    B = L.pop()
    while L:
        T = L.pop()

        minCross = sys.maxint
        chosenPerm = T
        for P in itertools.permutations(T):  # permute level assignment and chose will least crossings
            crossing = 0

            for ((ui, u), (vi, v)) in itertools.combinations(enumerate(P), 2):
                Eu = toIndex(N[u]['out'] + N[u]['in'], B)   # get indices for edges from and to level 2
                Ev = toIndex(N[v]['out'] + N[v]['in'], B)   # get indices for edges from and to level 2

                for uc_i, vc_i in itertools.product(Eu, Ev):
                    #print 'uc_i: {}, vc_i: {}'.format(uc_i, vc_i)
                    if uc_i > vc_i:     # (s, d) if destination of u edge is further than destination of v edge:
                        crossing += 1

            #print 'Permutation: {}, Cnt: {}'.format(P, crossing)
            if crossing < minCross:
                minCross = crossing
                chosenPerm = P

        #print 'minCrossing: {}, for Permutation: {} with pairs (T, B) = ({}, {})\n'.format(minCross, chosenPerm, [x for x in T], [x for x in B])
        B = chosenPerm   # normally B = T for next pair, but we have use chosen an optimal permutation
        R += [ [x for x in B] ] # append permutation with least crosses

    return [ x for x in reversed(R) ]

def sugiyama(G):
    S = cycleAnalysis(G)
    N = invertBackEdges(G, S)   # invertierte Kanten braucht man nicht speichern, man nimmt einfahc den original graph..
    L = levelAssignment(N)
    N, L_b = getInBetweenNodes(G, L)    # no backedges in N
    R = minCrossing(N, L)
    return N, R

if  __name__=='__main__':
    #for i in pyramid(['a', 'b', 'c','d']):
    #    print i
    #exit()
    #edges = [(1, 3), (1, 4), (2, 6), (3, 2), (3, 7), (3, 8), (4, 5), (4, 6), (4, 8), (4, 9), (6, 10), (7, 10), (7, 11), (8, 7), (9, 11), (10, 12), (11, 12)]
    edges = [ ('A', 'B'), ('A', 'E'), ('B', 'C'), ('C', 'D'), ('D', 'C'), ('A', 'C')]
    #edges = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6), (6, 7), (5, 7) ]
    G = graphFromEdges(edges)

    printGraph(G)
    S = cycleAnalysis(G)
    G_inv = invertBackEdges(G, S)   # invertierte Kanten braucht man nicht speichern, man nimmt einfahc den original graph..
    L = levelAssignment(G_inv)
    G_inv, L_b = getInBetweenNodes(G_inv, L)
    print G_inv
    print L
    #print S
    #print 'popCrossing:'
    P = minCrossing(G_inv, L)
    print P
