#ref: http://ownagezone.wordpress.com/2013/02/25/sssps-shortest-path-algorithm-python-implementation/
import sys
if __name__ == '__main__':
    import os
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 os.pardir))
from map import Map


class Navigation:
    DELIM = "||"
    REACHED_RANGE = 50  # 0.5 meters
    INSTRUCTION = "Heading towards ID {0}, at your {1} {2:.0f} degrees and {3:.0f} meters away"
    ARRIVED_NOTIFICATION = "You have arrived the destination {0}"

    #Flyweight pattern
    __route = {}

    def __init__(self, building, level, start, end):
        self.building = building
        self.level = level
        self.start = start
        self.end = end
        startPoint = Map.get_node_by_location_name(building, level, start)
        self.pos = [float(startPoint["x"]), float(startPoint["y"])]
        self.nextLoc = {}

    @classmethod
    def flush_cache(cls):
        cls.__route = {}
        return

    def update_pos_by_dist_and_dir(self, distance, direction):
        """
        params:
        distance - distance went through
        direction - angles relative to the south (clockwise)
        """
        (x, y, newDir) = Map.get_direction_details(self.building, self.level, distance, direction)
        self.update_pos(x, y)

    def update_pos(self, deltaX, deltaY):
        self.pos[0] += deltaX
        self.pos[1] += deltaY
        return self.pos

    def get_pos(self):
        return self.pos

    def _sssp(self, graph):
        """calculate single source shortest path"""
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
        """get calculated sssp"""
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

    def get_next_location(self, x, y):
        """
        params: current x, and current y
        get the nearest node, and based on it, decide the next location
        """

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
        for location_name in route:
            node = Map.get_node_by_location_name(self.building,
                                                 self.level, location_name)
            distance = Map.get_distance(node["x"], x, node["y"], y)
            if distance < minDist:
                minDist = distance
                minDistNode = node
                routeIdxOfMinDistNode = idx
            idx += 1

        # decide the next location to return
        if routeIdxOfMinDistNode == 0:
        # if the nearest node is at the start point
        # return next node
            return Map.get_node_by_location_name(self.building,
                                                 self.level, route[1])
        elif routeIdxOfMinDistNode == routeLength - 1:
        # if is at the end point
        # return end node
            return minDistNode
        else:
        # is at point between start & end
        # prevNode ----- minDistNode (nearest node) ----- nextNode
            prevNode = Map.get_node_by_location_name(self.building, self.level,
                                                     route[routeIdxOfMinDistNode - 1])
            nextNode = Map.get_node_by_location_name(self.building, self.level,
                                                     route[routeIdxOfMinDistNode + 1])
            prevDist = Map.get_distance(prevNode["x"], x, prevNode["y"], y)
            nextDist = Map.get_distance(nextNode["x"], x, nextNode["y"], y)
            if nextDist <= prevDist:
            # if nearer to the next node
            # return next node
                return nextNode
            else:
            # nextDist > prevDist -- nearer to the previous node
                if self.is_reach_node(minDistNode, x, y):
                # already reached the nearest node
                # return next node
                    return nextNode
                else:
                # else return the nearest node
                    return minDistNode

    def get_next_location_details(self, direction, x, y):
        """
        params:
        current user's direction (relative to north 0~360d), current x & y pos
        return:
        distance to next loc, direction to next loc (relative to user) & next loc's node
        """
        nextLocNode = self.get_next_location(x, y)
        self.nextLoc = nextLocNode
        dist = Map.get_distance(nextLocNode["x"], x, nextLocNode["y"], y)

        northAt = Map.get_north_at(self.building, self.level)
        userDir = direction + northAt  # relative to map
        if userDir > 360:
            userDir -= 360
        movingDir = Map.get_direction(x, nextLocNode["x"],
                                      y, nextLocNode["y"])  # relative to map
        relativeDir = movingDir - userDir
        # if relativeDir > 0, it's at user's rhs, else lhs
        if relativeDir > 180:
            relativeDir -= 360
        if relativeDir < -180:
            relativeDir += 360

        return relativeDir, dist, nextLocNode

    def get_next_location_by_direction(self, direction):
        return self.get_next_location_details(direction, self.pos[0], self.pos[1])

    def get_next_instruction(self, direction):
        """
        param: direction relative to the South
        """
        dirRelativeNorth = Map.get_direction_relative_north(self.building, self.level, direction)
        relativeDir, dist, nextLocNode = self.get_next_location_by_direction(dirRelativeNorth)
        side = "right hand side" if relativeDir >= 0 else "left hand side"
        return Navigation.INSTRUCTION.format(nextLocNode['nodeId'], side, abs(relativeDir), dist / 100.0)

    def is_reach_end(self):
        return self.is_reach_location(self.end, self.pos[0], self.pos[1])

    def is_reach_location(self, location_name, x, y):
        """current x, and current y"""
        node = Map.get_node_by_location_name(self.building,
                                             self.level, location_name)
        return self.is_reach_node(node, x, y)

    def is_reach_node(self, node, x, y):
        """current x, and current y"""
        distance = Map.get_distance(node["x"], x, node["y"], y)
        return distance <= Navigation.REACHED_RANGE

    def is_reach_next_location(self):
        if not self.nextLoc:
            return False
        return self.is_reach_node(self.nextLoc, self.pos[0], self.pos[1])

SPEAK_STRING = "Turn {0:.0f} degrees and walk {1:.0f} metres. You are heading towards {2}"

if __name__ == '__main__':
    print "show the route: from Entrance to TO level 2"
    print Navigation("DemoBuilding", "1",
                     "Entrance",
                     "TO level 2").get_route()
    print "-------------------------------------------"
    # next: corridor
    print "show next loc: for pos (600, 250) -- corridor"
    print Navigation("DemoBuilding", "1",
                     "Entrance",
                     "TO level 2").get_next_location(600, 250)
    print "-------------------------------------------"
    # next: to lvl 2
    print "show next loc: for pos (750, 300) -- to lvl 2"
    print Navigation("DemoBuilding", "1",
                     "Entrance",
                     "TO level 2").get_next_location(750, 300)
    print "-------------------------------------------"
    print "show next loc details: for pos (750, 300) -- dist 50, angle 0d"
    result = Navigation("DemoBuilding", "1",
                        "Entrance",
                        "TO level 2").get_next_location_details(270, 750, 300)
    print result
    print "-------------------------------------------"
    print "set up, get and update position"
    nav = Navigation("DemoBuilding", "1",
                     "Entrance",
                     "TO level 2")
    print nav.get_pos()
    print nav.update_pos(100, 50)
    print nav.is_reach_next_location()
    print nav.get_next_instruction(270)
    print nav.update_pos(100, -50)
    print nav.is_reach_next_location()
    print nav.get_next_instruction(270)
    print nav.update_pos(100, -50)
    print nav.is_reach_next_location()
    print nav.get_next_instruction(270)

    from Speech.espeak_api import VoiceOutput
    voice = VoiceOutput()
    voice.speak(SPEAK_STRING.format(result[0], result[1] / 100.0, result[2]['nodeName']))
    result = Navigation('Com1', "2", "P2", "P10").get_next_location_details(90, 1500, 1260)
    print result
    voice.speak(SPEAK_STRING.format(result[0], result[1] / 100.0, result[2]['nodeName']))
    result = Navigation('Com1', "2", "P2", "TO Canteen").get_next_location_details(90, 1500, 1260)
    print result
    voice.speak(SPEAK_STRING.format(result[0], result[1] / 100.0, result[2]['nodeName']))
    result = Navigation('Com1', "2", "P2", "TO Canteen").get_next_location_details(90, 5600, 490)
    print result
    voice.speak(SPEAK_STRING.format(result[0], result[1] / 100.0, result[2]['nodeName']))
