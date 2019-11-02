from class4pgm.base_model import BaseModel
from class4pgm.util import quote_string


class Node(object):
    def __init__(self, labels=None, properties=None, _id=None):
        self._id = _id
        self.labels = labels
        self.properties = properties

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


class NodeModel(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def convert(self):
        return {
            "labels": self.get_labels(),
            "properties": self.get_properties()
        }

    def __str__(self):
        return '(' + self.print_body() + ')'
