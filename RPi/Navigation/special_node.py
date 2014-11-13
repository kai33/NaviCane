class SpecialNode:
    nodes = {
        'com1-2-26',  # COM1~COM2 junction
        'com2-2-6',  # COM2-2 junction
        'com2-2-13',  # another door, just bf stairwell
        'com2-2-14'  # stairwell
    }

    @classmethod
    def is_special_node(cls, building, level, node):
        return (building + "-" + level + "-" + node['nodeId']).lower() in cls.nodes

if __name__ == '__main__':
    print ('COM1-2-26').lower() in SpecialNode.nodes
