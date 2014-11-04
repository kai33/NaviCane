import sys
if __name__ == '__main__':
    import os
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 os.pardir))
from Navigation.navigation import Navigation
from Navigation.map import Map


class Guidance:
    def __init__(self, startBuilding, startLevel, startId, endBuilding, endLevel, endId):
        self.startBuilding = startBuilding
        self.startLevel = startLevel
        self.startId = startId
        self.endBuilding = endBuilding
        self.endLevel = endLevel
        self.endId = endId

    def is_same_map(self):
        return (self.startBuilding == self.endBuilding) and (self.startLevel == self.endLevel)

    """ simply BFS """
    def get_map_route(self):
        visited = set()
        visited.add(self.startBuilding + "-" + self.startLevel)
        queue = [self.startBuilding + "-" + self.startLevel]
        parent = {}
        while queue:
            u = queue.pop(0)
            building, level = u.split("-")
            connectedMaps = Map.get_connected_maps(building, level)
            for map in connectedMaps:
                nextBuilding, nextLevel, nextId = map.split("-")
                if (nextBuilding + "-" + nextLevel) not in visited:
                    visited.add(nextBuilding + "-" + nextLevel)
                    queue.append(nextBuilding + "-" + nextLevel)
                    parent[nextBuilding + "-" + nextLevel] = building + "-" + level
        route = [self.endBuilding + "-" + self.endLevel]
        tmp = self.endBuilding + "-" + self.endLevel
        print parent
        while tmp != (self.startBuilding + "-" + self.startLevel):
            route.append(parent[tmp])
            tmp = parent[tmp]
        route.reverse()
        return route

    def get_nav(self):
        nav = []
        if(self.is_same_map()):
            startName = Map.get_node_by_location_id(self.startBuilding, self.startLevel, self.startId)['nodeName']
            endName = Map.get_node_by_location_id(self.endBuilding, self.endLevel, self.endId)['nodeName']
            nav.append(Navigation(self.startBuilding, self.startLevel, startName, endName).get_route())
        else:
            mapRoute = self.get_map_route()
            mapRouteIdx = 0
            for map in mapRoute:
                building, level = map.split("-")
                startName = ""
                endName = ""
                if mapRouteIdx == 0:
                    startName = Map.get_node_by_location_id(self.startBuilding, self.startLevel, self.startId)['nodeName']
                    endName = Map.get_node_by_connected_map(self.startBuilding, self.startLevel, mapRoute[mapRouteIdx + 1])['nodeName']
                elif mapRouteIdx == (len(mapRoute) - 1):
                    startName = Map.get_node_by_connected_map(self.endBuilding, self.endLevel, mapRoute[mapRouteIdx - 1])['nodeName']
                    endName = Map.get_node_by_location_id(self.endBuilding, self.endLevel, self.endId)['nodeName']
                else:
                    startName = Map.get_node_by_connected_map(building, level, mapRoute[mapRouteIdx - 1])['nodeName']
                    endName = Map.get_node_by_connected_map(building, level, mapRoute[mapRouteIdx + 1])['nodeName']
                nav.append(Navigation(building, level, startName, endName))
                mapRouteIdx += 1
        return nav


if __name__ == '__main__':
    Guidance("COM1", "2", "1", "COM1", "2", "4").get_nav()
    nav = Guidance("COM1", "2", "28", "COM2", "3", "1").get_nav()
    for n in nav:
        print n.get_route()
        