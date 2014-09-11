#ref: http://ownagezone.wordpress.com/2013/02/25/sssps-shortest-path-algorithm-python-implementation/
import sys
def sssp(graph, start, end):
    infinity = sys.maxint
    distance = dict([(vertex, infinity) for vertex in graph])
    distance[start] = 0
    parent = dict([(vertex, None) for vertex in graph])
    pqueue = graph.keys()

    #vertex comparator function
    def vertexComparator(v):
        return distance[v]
    
    while pqueue != []:
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

#TODO: separate data into id-name dict & name-distance dict
graph = {
    'Entrance' : [('Room 1',200)],
    'Room 1' : [('Room 2', 100)],
    'Room 2' : [('Male Toilet', 200), ('Room 3', 300)],
    'Male Toilet' : [('Corridor', 100)],
    'Female Toilet' : [('Room 3', 200),('Corridor', 200)],
    'Corridor' : [('Male Toilet', 100),('Female Toilet', 200),('TO level 2', 200)],
    'TO level 2' : [('Corridor', 200)],
    'Room 3' : [('Room 2', 300), ('Female Toilet', 200)]
    }

traverse = sssp(graph,'Entrance','TO level 2')
print traverse