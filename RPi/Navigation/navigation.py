#ref: http://ownagezone.wordpress.com/2013/02/25/sssps-shortest-path-algorithm-python-implementation/
import sys
if __name__ == '__main__':
    import os
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 os.pardir))
from map import Map

class Navigation:
    DELIM = "||"
    REACHED_RANGE = 25

    #Flyweight pattern
    __route = {}

    def __init__(self, building, level, start, end):
        self.building = building
        self.level = level
        self.start = start
        self.end = end

    def _sssp(self, graph): # single source shortest path
        infinity = sys.maxint
        distance = dict([(vertex, infinity) for vertex in graph])
        distance[self.start] = 0
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
        route = [self.end]
        tmp = self.end
        while tmp != self.start:
            route.append(parent[tmp])
            tmp = parent[tmp]
        route.reverse()
        return route

    def get_route(self):
        route = Navigation.__route.get(self.building + Navigation.DELIM +
                                self.level + Navigation.DELIM +
                                self.start + Navigation.DELIM +
                                self.end, None)
        if route is None:
            graph = Map.get_graph(self.building, self.level)
            route = self._sssp(graph)
            #cache route data
            Navigation.__route[self.building + Navigation.DELIM +
                        self.level + Navigation.DELIM +
                        self.start + Navigation.DELIM +
                        self.end] = route
        return route

    def get_next_location(self, x, y): #current x, and current y
        # get the nearest node, and based on it, decide the next location

        route = self.get_route()
        routeLength = len(route)
        # base cases:
        if routeLength == 1:
            return Map.get_node_by_location_name(route[0])
        elif routeLength == 2:
            return Map.get_node_by_location_name(route[1])

        minDist = sys.maxint
        minDistNode = {}
        routeIdxOfMinDistNode = -1

        # get the nearest node
        idx = 0
        for locationName in route:
            node = Map.get_node_by_location_name(self.building, self.level, locationName)
            distance = Map.get_distance(node["x"], x, node["y"], y)
            if distance < minDist:
                minDist = distance
                minDistNode = node
                routeIdxOfMinDistNode = idx
            idx += 1

        # decide the next location to return
        if routeIdxOfMinDistNode == 0: # the nearest node is at the start point
            return Map.get_node_by_location_name(self.building, self.level, route[1]) # return next node
        elif routeIdxOfMinDistNode == routeLength - 1: # is at the end point
            return minDistNode # return end node
        else: # is at point between start & end
            # prevNode ----- minDistNode (nearest node) ----- nextNode
            prevNode = Map.get_node_by_location_name(self.building, self.level, route[routeIdxOfMinDistNode - 1])
            nextNode = Map.get_node_by_location_name(self.building, self.level, route[routeIdxOfMinDistNode + 1])
            prevDist = Map.get_distance(prevNode["x"], x, prevNode["y"], y)
            nextDist = Map.get_distance(nextNode["x"], x, nextNode["y"], y)
            if nextDist <= prevDist: # if nearer to the next node
                return nextNode # return next node
            else: # nextDist > prevDist -- nearer to the previous node
                if is_reach_node(minDistNode, x, y): # already reached the nearest node
                    return nextNode #return next node
                else:
                    return minDistNode #return the nearest node

    def is_reach_end(self, x, y): #current x, and current y
        return self.is_reach_location(self.end, x, y)

    def is_reach_location(self, locationName, x, y): #current x, and current y
        node = Map.get_node_by_location_name(self.building, self.level, locationName)
        return is_reach_node(node, x, y)

    def is_reach_node(self, node, x, y): #current x, and current y
        distance = Map.get_distance(node["x"], x, node["y"], y)
        return distance <= Navigation.REACHED_RANGE

if __name__ == '__main__':
    print Navigation("DemoBuilding", "1", "Entrance", "TO level 2").get_next_location(200, 100) # next: room 1
    print Navigation("DemoBuilding", "1", "Entrance", "TO level 2").get_next_location(300, 100) # next: room 1
    print Navigation("DemoBuilding", "1", "Entrance", "TO level 2").get_next_location(350, 100) # next: room 2
    print Navigation("DemoBuilding", "1", "Entrance", "TO level 2").get_next_location(400, 150) # next: room 2
    print Navigation("DemoBuilding", "1", "Entrance", "TO level 2").get_next_location(500, 200) # next: mt
    print Navigation("DemoBuilding", "1", "Entrance", "TO level 2").get_next_location(600, 250) # next: corridor
    print Navigation("DemoBuilding", "1", "Entrance", "TO level 2").get_next_location(750, 300) # next: to lvl 2

