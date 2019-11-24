import re

from class4pgm.field import Field


class BaseModel(object):

    def __init__(self, _alias=None, _id=None, **kwargs):
        self._alias = _alias
        self._id = _id
        classes = self.get_inheritances()
        for clazz in classes:
            self._assign(clazz, kwargs)

    def _assign(self, clazz: type, kwargs: dict):
        for name, field in vars(clazz).items():
            if isinstance(field, Field):
                value = kwargs.get(name, None)
                self.__dict__[name] = value

    def get_inheritances(self):
        visited = set()
        q = [self.__class__]
        res = [self.__class__]
        while len(q) > 0:
            new_q = []
            for clazz in q:
                for parent_class in clazz.__bases__:
                    if parent_class in visited:
                        continue
                    new_q.append(parent_class)
                    res.append(parent_class)
                    visited.add(parent_class)
            q = new_q
        return res

    def get_alias(self):
        return self._alias

    def get_id(self):
        return self._id

    def get_properties(self):
        """ Returns a dictionary of all attributes of the Model which
            are not preceded by underscores.

        Returns:
            dict
        """
        pattern = "^_+.*"  # Pattern which matches "_attribute"
        prop = {}
        variables = vars(self)

        for var in variables:
            if not re.search(pattern, var):
                value = variables[var]
                if value is None:
                    continue
                prop[var] = variables[var]

        return prop
