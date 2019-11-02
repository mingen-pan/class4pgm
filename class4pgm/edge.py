from class4pgm.base_model import BaseModel
from class4pgm.node import Node
from class4pgm.util import quote_string


class Edge:
    def __init__(self, in_node: Node, out_node: Node, labels: list = None, properties: dict = None, _id=None):
        self._id = _id
        self.in_node = in_node
        self.out_node = out_node
        self.labels = labels
        self.properties = properties

    def __str__(self):
        """
        Copy from RedisGraph
        :return:
        """
        res = ['-[']
        if self.labels:
            res.append(':' + ":".join(self.labels))
        if self.properties:
            props = ','.join(key + ':' + str(quote_string(val)) for key, val in self.properties.items())
            res.append(' {' + props + '} ')
        res += ']->'

        return ''.join(res)


class EdgeModel(BaseModel):
    def __init__(self, in_node, out_node, **kwargs):
        self.in_node = in_node
        self.out_node = out_node
        super().__init__(**kwargs)

    def convert(self):
        return {
            "in_node": self.in_node,
            "out_node": self.out_node,
            "labels": self.get_labels(),
            "properties": self.get_properties()
        }

    def __str__(self):
        return '-[' + self.print_body() + ']->'
