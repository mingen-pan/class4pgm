from class4pgm import NodeModel
from class4pgm.base_model import BaseModel
from class4pgm.util import quote_string


class EdgeModel(BaseModel):
    def __init__(self, in_node, out_node, **kwargs):
        self._in_node = in_node
        self._out_node = out_node
        self._relationship = self.__class__.__name__
        super().__init__(**kwargs)

    def get_in_node(self):
        return self._in_node

    def get_out_node(self):
        return self._out_node

    def get_relationship(self):
        return self._relationship

        # return '-[' + self.print_body() + ']->'

    def __str__(self):
        res = []
        if isinstance(self._in_node, NodeModel):
            res.append(str(self._in_node))
        else:
            res.append('()')

        res.append('-[')
        if self._relationship:
            res.append(':' + self._relationship)
        props = self.get_properties()
        if props:
            prop_str = ','.join(key + ':' + str(quote_string(val)) for key, val in props.items())
            res.append(' {' + prop_str + '}')
        res.append(']->')

        if isinstance(self._out_node, NodeModel):
            res.append(str(self._out_node))
        else:
            res.append('()')

        return ''.join(res)
