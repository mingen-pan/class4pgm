from collections import deque

from class4pgm.base_model import BaseModel
from class4pgm.util import quote_string


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


class NodeModel(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._labels = self.get_labels()

    def convert(self):
        return {
            "labels": self._labels,
            "properties": self.get_properties()
        }

    def __str__(self):
        return '(' + self.print_body() + ')'

    def get_labels(self):
        labels = []
        explored = set()
        to_explore = deque()
        to_explore.append(type(self))
        while len(to_explore) > 0:
            cur = to_explore.popleft()
            if cur in explored or cur is NodeModel:
                continue
            explored.add(cur)
            labels.append(cur.__name__)
            to_explore.extend(cur.__bases__)
        return labels

    def print_body(self):
        res = []
        if self._labels:
            res.append(':' + ":".join(self._labels))
            props = self.get_properties()
            prop_str = ','.join(key + ':' + str(quote_string(val)) for key, val in props.items())
            res.append(' {' + prop_str + '}')

        return ''.join(res)
