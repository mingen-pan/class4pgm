from class4pgm.util import quote_string, random_string


class Node(object):
    def __init__(self, alias=None, labels: list = None, properties: dict = None, _id=None):
        if labels is None:
            labels = []
        if properties is None:
            properties = {}
        self.alias = alias
        self._id = _id
        self.labels = labels
        self.properties = properties

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = val

    def __str__(self):
        """
        Copy from RedisGraph
        :return:
        """
        res = ['(']
        if self.labels:
            res.append(':' + ":".join(self.labels))
        if self.properties:
            props = ','.join(key + ':' + str(quote_string(val)) for key, val in self.properties.items())
            res.append(' {' + props + '} ')
        res += ')'

        return ''.join(res)


class Edge:
    def __init__(self, in_node, relationship: str, out_node,
                 alias=None, properties=None, _id=None):
        self.in_node = in_node
        self.relationship = relationship
        self.out_node = out_node
        self.alias = alias
        self._id = _id
        self.properties = properties

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = val

    def __str__(self):
        """
        Copy from RedisGraph
        :return:
        """
        res = ['-[']
        if self.relationship:
            res.append(':' + self.relationship)
        if self.properties:
            props = ','.join(key + ':' + str(quote_string(val)) for key, val in self.properties.items())
            res.append(' {' + props + '} ')
        res += ']->'

        return ''.join(res)


class Graph(object):
    def __init__(self, name):
        """
        Create a new graph.
        """
        self.name = name
        self.aliases = set()
        self.nodes = {}
        self.edges = {}
        self.class_definitions = {}

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

    def add_class_definition(self, definition: Node):
        if definition.properties["class_name"] not in self.class_definitions:
            self.class_definitions[definition.properties["class_name"]] = definition
            return True
        else:
            return False
