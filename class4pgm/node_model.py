from collections import deque

from class4pgm.base_model import BaseModel
from class4pgm.util import quote_string


class NodeModel(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._labels = self.get_labels()

    def convert(self):
        return {
            "labels": self._labels,
            "properties": self.get_properties()
        }

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

    def __str__(self):
        res = ['(']
        if self._alias:
            res.append(self._alias)
        if self._labels:
            res.append(':' + ":".join(self._labels))
        props = self.get_properties()
        if props:
            prop_str = ','.join(key + ':' + str(quote_string(val)) for key, val in props.items())
            res.append(' {' + prop_str + '}')
        res.append(')')
        return ''.join(res)
