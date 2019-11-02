import json

datatype_dict = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list
}


def datatype_encoder(datatype: type):
    return datatype.__name__


def datatype_decoder(s: str):
    if s in datatype_dict:
        return datatype_dict[s]
    return None


class Field(object):
    def __init__(self, datatype: type, nullable: bool = True, unique: bool = False,
                 exception: bool = False):
        self.datatype = datatype
        self.nullable = nullable
        self.unique = unique
        self.exception = exception

    def __str__(self):
        return str(self.__dict__)

    def encode(self):
        properties = self.__dict__.copy()
        properties['datatype'] = datatype_encoder(properties['datatype'])
        return properties

    @classmethod
    def decode(cls, params: dict):
        params['datatype'] = datatype_decoder(params['datatype'])
        return cls(**params)

    def validate(self, value):
        if not value:
            if self.nullable:
                return value
            self.raise_exception("null is not allowed")
            return

        if not isinstance(value, self.datatype):
            self.raise_exception("datatype does not match")
            return

        return value

    def raise_exception(self, msg: str):
        if self.exception:
            raise ValueError(msg)


def Int(nullable: bool = True, unique: bool = False, exception: bool = True):
    return Field(int, nullable, unique, exception)


def Float(nullable: bool = True, unique: bool = False, exception: bool = True):
    return Field(float, nullable, unique, exception)


def String(nullable: bool = True, unique: bool = False, exception: bool = True):
    return Field(str, nullable, unique, exception)


def Bool(nullable: bool = True, unique: bool = False, exception: bool = True):
    return Field(bool, nullable, unique, exception)


def List(nullable: bool = True, unique: bool = False, exception: bool = True):
    return Field(list, nullable, unique, exception)
