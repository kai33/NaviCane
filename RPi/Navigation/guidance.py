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
        self.nav = []
        self.navIdx = 0

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
        while tmp != (self.startBuilding + "-" + self.startLevel):
            route.append(parent[tmp])
            tmp = parent[tmp]
        route.reverse()
        return route

    def get_nav(self):
        if self.nav:
            return self.nav
        if(self.is_same_map()):
            startName = Map.get_node_by_location_id(self.startBuilding, self.startLevel, self.startId)['nodeName']
            endName = Map.get_node_by_location_id(self.endBuilding, self.endLevel, self.endId)['nodeName']
            self.nav.append(Navigation(self.startBuilding, self.startLevel, startName, endName).get_route())
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
                self.nav.append(Navigation(building, level, startName, endName))
                mapRouteIdx += 1
        return self.nav

    def get_next_instruction(self, dir):
        currentNav = self.get_nav()[self.navIdx]
        isReachEnd = currentNav.is_reach_end()
        if isReachEnd:
            self.navIdx += 1
        return currentNav.get_next_instruction(dir)

    def update_pos_by_dist_and_dir(self, dist, dir):
        currentNav = self.get_nav()[self.navIdx]
        return currentNav.update_pos_by_dist_and_dir(dist, dir)

    def get_pos(self):
        currentNav = self.get_nav()[self.navIdx]
        return currentNav.get_pos()

    def get_next_loc(self):
        currentNav = self.get_nav()[self.navIdx]
        return currentNav.nextLoc

    def is_reach_next_location(self):
        currentNav = self.get_nav()[self.navIdx]
        return currentNav.is_reach_next_location()

    def is_reach_end(self):
        currentNav = self.get_nav()[self.navIdx]
        isReachEnd = currentNav.is_reach_end()
        if isReachEnd:
            self.navIdx += 1
        return isReachEnd

if __name__ == '__main__':
    Guidance("COM1", "2", "1", "COM1", "2", "4").get_nav()
    guide = Guidance("COM1", "2", "28", "COM2", "3", "1")
    nav = guide.get_nav()
    for n in nav:
        print n.get_route()
    # to P29
    print guide.get_next_instruction(10)
    print guide.get_next_instruction(10)
    guide.update_pos_by_dist_and_dir(500, 270)
    print guide.get_next_instruction(10)
    print guide.get_next_instruction(10)
    print guide.get_pos()
    print guide.is_reach_next_location()
    print guide.get_next_loc()
    # to TO COM2-2-1
    print guide.get_next_instruction(10)
    print guide.get_next_instruction(10)
    guide.update_pos_by_dist_and_dir(500, 270)
    print guide.get_next_instruction(10)
    print guide.get_next_instruction(10)
    print guide.get_pos()
    print guide.is_reach_next_location()
    print guide.get_next_loc()
    # to TO COM2-2-1
    print guide.get_next_instruction(10)
    print guide.get_next_instruction(10)
    guide.update_pos_by_dist_and_dir(320, 220)
    print guide.get_next_instruction(10)
    print guide.get_next_instruction(10)
    print guide.get_pos()
    print guide.is_reach_next_location()
    print guide.get_next_loc()
