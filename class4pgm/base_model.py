import re
from collections import deque

from class4pgm.util import quote_string


class BaseModel(object):
    def __init__(self, **kwargs):
        self._labels = self.get_labels()
        self._properties = self.get_properties()

    def get_labels(self):
        labels = []
        explored = set()
        to_explore = deque()
        to_explore.append(type(self))
        while len(to_explore) > 0:
            cur = to_explore.popleft()
            if cur in explored or cur.__base__ is BaseModel:
                continue
            explored.add(cur)
            labels.append(cur.__name__)
            to_explore.extend(cur.__bases__)
        return labels

    def get_properties(self):
        """ Returns a dictionary of all attributes of the Atom which
            are not preceded by underscores.

        Parameters:
            None

        Raises:
            None

        Returns:
            dict
        """
        pattern = "^_+.*"  # Pattern which matches "_attribute"
        prop = {}
        variables = vars(self)

        for var in variables:
            if not re.search(pattern, var):
                prop[var] = variables[var]

        return prop

    def print_body(self):
        res = []
        if self._labels:
            res.append(':' + ":".join(self._labels))
        if self._properties:
            props = ','.join(key + ':' + str(quote_string(val)) for key, val in self._properties.items())
            res.append(' {' + props + '}')

        return ''.join(res)
