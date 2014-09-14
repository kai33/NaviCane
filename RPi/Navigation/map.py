import math
if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 os.pardir))
from Communication.WiFi.internet_access import get_floor_plan

class Map:
	DELIM = "||"

	#Flyweight pattern
	__map = {}
	__graph = {}

	@classmethod
	def get_map(cls, building, level):
		print "get map data for " + building + " level " + level

		data = cls.__map.get(building + cls.DELIM + level, None)
		if data is None:
			data = get_floor_plan(building, level)
			#cache map data
			cls.__map[building + cls.DELIM + level] = data
		return data

	@classmethod
	def get_graph(cls, building, level):
		print "get graph data for " + building + " level " + level

		data = cls.__graph.get(building + cls.DELIM + level, None)
		if data is None:
			# generate graph data from raw data
			rawData = cls.get_map(building, level)
			mapData = rawData["map"]
			data = {}
			for node in mapData:
				#graph data (an adjacent list) format:
				#key - node name
				#value - a list of adjacent nodes' names & their distances to the key's node
				data[node["nodeName"]] = []
				adjNodeIds = node["linkTo"].split(", ")
				for adjNodeIdInString in adjNodeIds:
					adjNodeId = int(adjNodeIdInString) - 1
					adjNode = mapData[adjNodeId]

					distance = cls.get_distance(adjNode["x"], node["x"], adjNode["y"], node["y"])
					nodeDistPair = (adjNode["nodeName"], distance)
					data[node["nodeName"]].append(nodeDistPair)
			#cache graph data
			cls.__graph[building + cls.DELIM + level] = data
		return data

	@classmethod
	def get_distance(cls, x1, x2, y1, y2):
		return math.sqrt(math.pow(int(x1) - int(x2), 2) + math.pow(int(y1) - int(y2), 2))

	@classmethod
	def flush_cache(cls):
		cls.__map = {}
		cls.__graph = {}
		return

if __name__ == '__main__':
	Map.get_map("DemoBuilding", "1") #downloading
	Map.get_map("DemoBuilding", "1") #cache
	Map.get_map("DemoBuilding", "1") #cache
	Map.get_map("DemoBuilding", "2") #downloading
	Map.get_map("DemoBuilding", "2") #cache
	Map.get_graph("DemoBuilding", "1")
	Map.flush_cache()
	Map.get_graph("DemoBuilding", "1")
