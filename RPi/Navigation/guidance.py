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
        if(self.is_same_map()):  # normal same-map navigation
            startName = Map.get_node_by_location_id(self.startBuilding, self.startLevel, self.startId)['nodeName']
            endName = Map.get_node_by_location_id(self.endBuilding, self.endLevel, self.endId)['nodeName']
            self.nav.append(Navigation(self.startBuilding, self.startLevel, startName, endName).get_route())
        else:  # inter-building or inter-level navigation
            mapRoute = self.get_map_route()
            mapRouteIdx = 0
            for map in mapRoute:
                building, level = map.split("-")
                startName = ""
                endName = ""
                if mapRouteIdx == 0:  # start map
                    startName = Map.get_node_by_location_id(self.startBuilding, self.startLevel, self.startId)['nodeName']  # start is given
                    endName = Map.get_node_by_connected_map(self.startBuilding, self.startLevel, mapRoute[mapRouteIdx + 1])['nodeName']
                elif mapRouteIdx == (len(mapRoute) - 1):  # end map
                    # print "the end"
                    prevNav = self.nav[mapRouteIdx - 1]
                    # print "prev nav end is " + prevNav.end
                    startId = self.extract_id_from_name(prevNav.end)
                    # print "id is " + startId
                    startName = Map.get_node_by_location_id(self.endBuilding, self.endLevel, startId)['nodeName']
                    # print "start name is " + startName
                    endName = Map.get_node_by_location_id(self.endBuilding, self.endLevel, self.endId)['nodeName']  # end is given
                else:  # in the mid
                    # print "in the mid"
                    prevNav = self.nav[mapRouteIdx - 1]
                    # print "prev nav end is " + prevNav.end
                    startId = self.extract_id_from_name(prevNav.end)
                    # print "id is " + startId
                    startName = Map.get_node_by_location_id(building, level, startId)['nodeName']
                    # print "start name is " + startName
                    endName = Map.get_node_by_connected_map(building, level, mapRoute[mapRouteIdx + 1])['nodeName']
                self.nav.append(Navigation(building, level, startName, endName))
                mapRouteIdx += 1
        return self.nav

    def extract_id_from_name(self, nodeName):
        if nodeName.lower().startswith("to ") and (len(nodeName.split("-")) == 3):
            return nodeName.split("-")[2]
        return -1

    def get_next_instruction(self, dir):
        route = self.get_nav()
        currentNav = route[self.navIdx]
        isReachEnd = currentNav.is_reach_end()
        nextInstr = ""
        if isReachEnd and self.navIdx + 1 < len(route):
            self.navIdx += 1
            currentNav = self.get_nav()[self.navIdx]
            nextInstr = "in " + currentNav.building + " level " + currentNav.level + " " + currentNav.get_next_instruction(dir)
        elif isReachEnd and self.navIdx + 1 == len(route):
            nextInstr = "reach the end"
        else:
            nextInstr = currentNav.get_next_instruction(dir)
        return nextInstr

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
        if self.navIdx == (len(self.get_nav()) - 1):
            lastNav = self.get_nav()[self.navIdx]
            return lastNav.is_reach_end()
        return False

if __name__ == '__main__':
    guide = Guidance("COM1", "2", "28", "COM2", "3", "1")
    nav = guide.get_nav()
    print "the navigation path is"
    for n in nav:
        print n.get_route()
    # start from p28, towards p26
    dir = 10
    print guide.get_next_instruction(dir)  # assume the start angle to be 10 deg
    print guide.get_next_instruction(dir)  # lhs 55 deg
    dir = dir - 55 + 360
    print guide.get_next_instruction(dir)  # turn left 55 deg
    print guide.get_next_instruction(dir)
    guide.update_pos_by_dist_and_dir(500, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards p29
    dir = dir - 87
    guide.update_pos_by_dist_and_dir(500, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards p31
    dir = dir + 43
    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 2 (next nav)
    dir = dir + 8
    guide.update_pos_by_dist_and_dir(2100, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 5
    guide.update_pos_by_dist_and_dir(500, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 6 (next nav)
    guide.update_pos_by_dist_and_dir(1500, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 11
    dir = dir - 90
    guide.update_pos_by_dist_and_dir(600, dir)
    print guide.is_reach_next_location()
    print guide.get_next_loc()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 12
    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 13
    dir = dir + 30
    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 14
    dir = dir - 36
    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 15
    dir = dir - 87
    guide.update_pos_by_dist_and_dir(600, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 16
    dir = dir - 70
    guide.update_pos_by_dist_and_dir(100, dir)
    print guide.is_reach_next_location()
    print guide.is_reach_end()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 10 (next nav)
    dir = dir - 106
    guide.update_pos_by_dist_and_dir(600, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 9
    dir = dir + 44
    guide.update_pos_by_dist_and_dir(150, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 8
    dir = dir + 60
    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 7
    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 2
    dir = dir - 18
    guide.update_pos_by_dist_and_dir(600, dir)
    print guide.is_reach_next_location()
    print guide.is_reach_end()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 1
    dir = dir + 90
    guide.update_pos_by_dist_and_dir(4000, dir)
    print guide.is_reach_next_location()
    print guide.is_reach_end()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)
    dir = dir + 53
    guide.update_pos_by_dist_and_dir(200, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)  # reach end
    print "test get pos"
    print guide.get_pos()
    print "test get next loc"
    print guide.get_next_loc()
    print guide.is_reach_end()
