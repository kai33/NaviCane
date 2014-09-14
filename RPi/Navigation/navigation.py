#ref: http://ownagezone.wordpress.com/2013/02/25/sssps-shortest-path-algorithm-python-implementation/
import sys
if __name__ == '__main__':
    import os
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 os.pardir))
from map import Map

def sssp(graph, start, end):
    infinity = sys.maxint
    distance = dict([(vertex, infinity) for vertex in graph])
    distance[start] = 0
    parent = dict([(vertex, None) for vertex in graph])
    pqueue = graph.keys()

    #vertex comparator function
    def vertexComparator(v):
        return distance[v]
    
    while pqueue:
        u = min(pqueue, key=vertexComparator)
        pqueue.remove(u)
        for v, weight in graph[u]:
            newDistance = distance[u] + weight
            #relax
            if newDistance < distance[v]:
                distance[v] = newDistance
                parent[v] = u
    #show my way
    route = [end]
    tmp = end
    while tmp != start:
        route.append(parent[tmp])
        tmp = parent[tmp]
    route.reverse()
    return route

if __name__ == '__main__':
    traverse = sssp(Map.get_graph("DemoBuilding", "1"),'Entrance','TO level 2')
    print traverse
