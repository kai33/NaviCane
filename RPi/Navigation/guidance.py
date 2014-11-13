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

    """
    simply run BFS to find out the connection between maps
    """
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

    """
    return an array of Navigation, starting from the start building/level/pt, ending at the end building/level/pt
    """
    def get_nav(self):
        if self.nav:
            return self.nav
        if(self.is_same_map()):  # normal same-map navigation
            startName = Map.get_node_by_location_id(self.startBuilding, self.startLevel, self.startId)['nodeName']
            endName = Map.get_node_by_location_id(self.endBuilding, self.endLevel, self.endId)['nodeName']
            self.nav.append(Navigation(self.startBuilding, self.startLevel, startName, endName))
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

    """
    the name of end node of previous map contains the node id of next map's starting point
    """
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

    def get_prev_loc(self):
        return self.get_nav()[self.navIdx].prevLoc

    def get_curr_building(self):
        return self.get_nav()[self.navIdx].building

    def get_curr_level(self):
        return self.get_nav()[self.navIdx].level

    def is_reach_next_location(self):
        currentNav = self.get_nav()[self.navIdx]
        return currentNav.is_reach_next_location()

    # used for calibration
    def reach_special_node(self, node):
        currentNav = self.get_nav()[self.navIdx]
        currentNav.pos[0] = node['x']
        currentNav.pos[1] = node['y']
        if node['nodeName'] not in currentNav.reachedLoc:
            currentNav.reachedLoc.append(node['nodeName'])

    def is_reach_end(self):
        if self.navIdx == (len(self.get_nav()) - 1):
            lastNav = self.get_nav()[self.navIdx]
            return lastNav.is_reach_end()
        return False

if __name__ == '__main__':
    dir = 10

    # pass when REACHED_RANGE = 10 (defined in navigation.py)
    simpleGuide = Guidance("COM2", "2", "5", "COM2", "2", "6")
    simpleGuide.update_pos_by_dist_and_dir(1000, dir)
    print simpleGuide.get_next_instruction(dir)
    print simpleGuide.get_next_instruction(dir)
    simpleGuide.update_pos_by_dist_and_dir(500, dir)
    print simpleGuide.get_pos()
    print simpleGuide.get_next_instruction(dir)
    print simpleGuide.get_next_instruction(dir)
    print simpleGuide.is_reach_next_location()
    print simpleGuide.is_reach_end()

    guide = Guidance("COM1", "2", "28", "COM2", "3", "1")
    nav = guide.get_nav()
    print "the navigation path is"
    for n in nav:
        print n.get_route()
    # TC pass when REACHED_RANGE = 150 (defined in navigation.py)
    # start from p28, towards p26
    print guide.get_next_instruction(dir)  # assume the start angle to be 10 deg
    print guide.get_next_instruction(dir)  # lhs 55 deg
    print guide.get_pos()

    print guide.get_next_instruction(dir)  # turn left 55 deg
    print guide.get_next_instruction(dir)
    guide.update_pos_by_dist_and_dir(700, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards p29
    print guide.get_pos()

    guide.update_pos_by_dist_and_dir(500, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards p31
    print guide.get_pos()

    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 2 (next nav)
    print guide.get_pos()

    guide.update_pos_by_dist_and_dir(2100, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 5
    print guide.get_pos()
    guide.update_pos_by_dist_and_dir(500, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 6 (next nav)
    print guide.get_pos()
    guide.update_pos_by_dist_and_dir(1500, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 11
    print guide.get_pos()

    guide.update_pos_by_dist_and_dir(600, dir)
    print guide.is_reach_next_location()
    print guide.get_next_loc()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 12
    print guide.get_pos()
    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 13
    print guide.get_pos()

    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 14
    print guide.get_pos()

    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 15
    print guide.get_pos()

    guide.update_pos_by_dist_and_dir(600, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 16
    print guide.get_pos()

    guide.update_pos_by_dist_and_dir(100, dir)
    print guide.is_reach_next_location()
    print guide.is_reach_end()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 10 (next nav)
    print guide.get_pos()

    guide.update_pos_by_dist_and_dir(600, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 9

    guide.update_pos_by_dist_and_dir(150, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 8

    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 7
    guide.update_pos_by_dist_and_dir(400, dir)
    print guide.is_reach_next_location()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 2

    guide.update_pos_by_dist_and_dir(600, dir)
    print guide.is_reach_next_location()
    print guide.is_reach_end()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)  # towards 1

    guide.update_pos_by_dist_and_dir(4000, dir)
    print guide.is_reach_next_location()
    print guide.is_reach_end()
    print guide.get_next_instruction(dir)
    print guide.get_next_instruction(dir)

    guide.update_pos_by_dist_and_dir(1000, dir)
    print guide.is_reach_next_location()
    print guide.is_reach_end()
    print guide.get_next_instruction(dir)  # reach end
    print "test get pos"
    print guide.get_pos()
    print "test get next loc"
    print guide.get_next_loc()
    print guide.is_reach_end()
