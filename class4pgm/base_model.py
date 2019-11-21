import re


class BaseModel(object):

    def __init__(self, _alias=None, _id=None, **kwargs):
        self._alias = _alias
        self._id = _id

    def get_alias(self):
        return self._alias

    def get_id(self):
        return self._id

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
