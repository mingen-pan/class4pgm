from class4pgm.edge import Edge
from class4pgm.node import Node
from class4pgm.util import random_string


class Graph(object):
    def __init__(self, name, redis_con):
        """
        Create a new graph.
        """
        self.name = name
        self.aliases = set()
        self.nodes = {}
        self.edges = {}

    def add_node(self, node: Node):
        while node.alias is None:
            alias = random_string()
            if alias not in self.aliases:
                self.aliases.add(alias)
                node.alias = alias
        self.nodes[node.alias] = node

    def add_edge(self, edge: Edge):
        """
        Addes an edge to the graph.
        """
        # Make sure edge both ends are in the graph
        assert self.nodes[edge.in_node.alias] is not None and self.nodes[edge.out_node.alias] is not None
        while edge.alias is None:
            alias = random_string()
            if alias not in self.aliases:
                self.aliases.add(alias)
                edge.alias = alias
        self.edges[edge.alias] = edge
