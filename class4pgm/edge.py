from class4pgm.base_model import BaseModel
from class4pgm.node import Node
from class4pgm.util import quote_string


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


class EdgeModel(BaseModel):
    def __init__(self, in_node, out_node, **kwargs):
        self._in_node = in_node
        self._out_node = out_node
        self._relationship = self.__class__.__name__
        super().__init__(**kwargs)

    def get_relationship(self):
        return self._relationship

    def __str__(self):
        return '-[' + self.print_body() + ']->'

    def print_body(self):
        res = []
        if self._relationship:
            res.append(':' + self._relationship)
        props = self.get_properties()
        prop_str = ','.join(key + ':' + str(quote_string(val)) for key, val in props.items())
        res.append(' {' + prop_str + '}')

        return ''.join(res)
