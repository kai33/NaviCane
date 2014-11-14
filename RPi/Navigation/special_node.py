class SpecialNode:
    nodes = {
        # 'com1-2-24',  # in front of seminar room 11
        # 'com1-2-26',  # bf COM1~COM2 connection
        'com1-2-18',  # in front of tr11
        'com2-2-6',  # COM2-2 junction towards stairwell
        'com2-2-13',  # another door, just bf stairwell
        'com2-2-14',  # start of stairwell (lvl2)
        'com2-3-10'  # end of stairwell (lvl3)
    }

    @classmethod
    def is_special_node(cls, building, level, node):
        return (building + "-" + level + "-" + node['nodeId']).lower() in cls.nodes

if __name__ == '__main__':
    print ('COM1-2-26').lower() in SpecialNode.nodes
