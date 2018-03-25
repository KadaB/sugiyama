#!/usr/bin/env python
# -*- coding: utf-8 -*-
def removeEdges(N, E):
    for s, d in E:
        if d in N[s]['out']:
            N[s]['out'].remove(d)

        if s in N[d]['in']:
            N[d]['in'].remove(s)

def insertEdges(N, E):
    for s, d in E:
        if not d in N[s]['out']:
            N[s]['out'].append(d)

        if not s in N[d]['in']:
            N[d]['in'].append(s)

def removeNode(N, n):
    if N.get(n) == None:
        return

    for p in N[n]['in']:    # for parent (remove all that have this as child)
        N[p]['out'].remove(n)

    for c in N[n]['out']:           # for child (remove all that have this as parent) 
        N[c]['in'].remove(n)

    del N[n]    # dictionary remove

def printGraph(N):
    for n in N:
        print '  ' + str(n)

        for e in N[n]:
            print '     {}: {}'.format(e, N[n][e])

def twistEdges(N, E):
    removeEdges(N, E)
    E_inv = [ (d, s) for s, d in E ]
    insertEdges(N, E_inv)

    return E_inv

def graphFromEdges(E):
    N = {}
    # node: in = [] out = []
    for e in E:
        s, d = e

        if N.get(s) == None:
            N[s] = {'in': [], 'out': []}

        if N.get(d) == None:
            N[d] = {'in': [], 'out': []}

        N[s]['out'].append(d)	# out
        N[d]['in'].append(s)	# in
    return N

if __name__ == '__main__':
    edges = [ ('A', 'B'), ('A', 'E'), ('B', 'C'), ('C', 'D'), ('D', 'C'), ('A', 'C')]
    printGraph(graphFromEdges(edges))
