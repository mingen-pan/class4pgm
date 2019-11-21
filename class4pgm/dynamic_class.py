from class4pgm.edge import EdgeModel
from class4pgm.field import Field
import json

import class4pgm.service.base_service as base_service
from class4pgm.node import NodeModel



def init_factory(instance_properties, parent_classes):
    """
    This is a factory function to generate __init__ of a dynamic class, based on the given
    instance_properties and parent_classes.
    instance_properties defines the field name of instance variables.

    For example, Given a Dynamic Class named `Student`
    `parent_classes = ["Person", "Learner"]`
    It will make the output __init__ to call the __init__ of its parent classes, which are `Person`
    and `Learner` in this example.

    `instance_properties = ["name", "age"]`
    the output __init__ will create name and age variables for the instances of a class.
    One can assign these values like
    `a = Student(name='Tom', age=26)`

    :param instance_properties: Set[String]
    :param parent_classes: List[String]
    :return: __init__ of a dynamic class
    """

    def init(self, **kwargs):
        for name, field in instance_properties.items():
            value = kwargs.pop(name, None)
            self.__dict__[name] = value
        for parent_class in parent_classes:
            parent_class.__init__(self, **kwargs)

    return init


class ClassDefinition:
    primitive_types = {int, float, str, bool}
    collection_types = {list, set, dict}

    def __init__(self, class_name, parent_classes, class_attributes, instance_properties):
        self.class_name = class_name
        self.parent_classes = parent_classes
        self.class_attributes = class_attributes
        self.instance_properties = instance_properties

    def wrap(self):
        class_attributes = json.loads(self.class_attributes)
        instance_properties = json.loads(self.instance_properties)
        return ClassDefinitionWrapper(self.class_name, self.class_attributes,
                                      class_attributes, instance_properties)

    @classmethod
    def resolve(cls, def_form):
        assert type(def_form) is type, "input must be a class/type"
        class_name = def_form.__name__
        parent_classes = []
        for parent in def_form.__bases__:
            parent_classes.append(parent.__name__)

        class_attributes = {}
        instance_properties = {}
        for key, value in vars(def_form).items():
            if len(key) > 2 and key[:2] == "__":
                continue
            if type(value) in cls.primitive_types:
                class_attributes[key] = value
            elif isinstance(value, Field):
                instance_properties[key] = value
        return cls(class_name=class_name, parent_classes=parent_classes, class_attributes=class_attributes,
                   instance_properties=instance_properties)


class ClassDefinitionWrapper(NodeModel):
    """
    Data Transfer Object (DTO) class for dynamic classes. The instances of this are used to store
    metadata of a class into graph databases. The metadata contain class name, parent classes,
    class variables, and instance variables. Only primitive types are allowed to persist for these
    metadata, i.e. number, string, bool, list, and dictionary. Dictionary should be stored as a json
    string.

    This DTO inherits Vertex of the GraphArcana ogm, which can be directly stored in graph databases.

    :param class_name: String
    :param parent_classes: List[String]
    :param class_attributes: Dictionary[String] -> Primitive Types
    :param instance_properties: Set or List of Strings

    """

    def __init__(self, class_name, parent_classes, class_attributes, instance_properties):
        self.class_name = class_name
        self.parent_classes = parent_classes
        self.class_attributes = class_attributes
        self.instance_properties = instance_properties
        self._attribute_check()
        super().__init__()

    def _attribute_check(self):
        assert isinstance(self.class_name, str) and len(self.class_name) > 0, \
            "class name is not string or empty"
        if not isinstance(self.parent_classes, list):
            self.parent_classes = []

        if not self.class_attributes:
            self.class_attributes = "{}"
        elif isinstance(self.class_attributes, str):
            try:
                json.loads(self.class_attributes)
            except ValueError as e:
                raise ValueError("class_attributes is not a valid JSON")
        elif isinstance(self.class_attributes, dict):
            self.class_attributes = json.dumps(self.class_attributes)
        else:
            raise ValueError("class_attributes should be JSON str or dict")

        if not self.instance_properties:
            self.instance_properties = "{}"
        elif isinstance(self.instance_properties, str):
            try:
                instance_properties = json.loads(self.instance_properties)
                for key, value in instance_properties.items():
                    Field.decode(value)
            except ValueError as e:
                raise ValueError("instance_properties is not a valid JSON")
        elif isinstance(self.instance_properties, dict):
            instance_properties = {}
            for name, field in self.instance_properties.items():
                assert isinstance(field, Field), "instance properties should be Field class only"
                instance_properties[name] = field.encode()
            self.instance_properties = json.dumps(instance_properties)

    def unpack(self):
        try:
            class_attributes = json.loads(self.class_attributes)
        except ValueError:
            raise ValueError("class_attributes is not a valid JSON")

        try:
            instance_properties = {
                key: Field.decode(value) for key, value in json.loads(self.instance_properties).items()
            }
        except ValueError:
            raise ValueError("instance_properties is not a valid JSON")

        return ClassDefinition(self.class_name, self.parent_classes, class_attributes, instance_properties)


class ClassManager:
    """
    A class to convert DynamicClassDTO instances to dynamic classes. It will resolve class inheritance
    based on Depth-first Search. It uses lazy initialization to build dynamic classes. They are built
    only when you call `get` or `build`.

    Attributes
    _______
    classes: Dict[string]Type
        A dictionary used to query classes by their names.

    Methods
    -------
    __init__(self, class_dto_list)
        take a list of dynamic class dtos to build a instance

    add(self, dto)
        Add individual dto

    build(self)
        build all the dynamic classes in this collection

    get(self, name)
        get the dynamic class with `name`. It will built this class and its parent classes automatically.
    """

    def __init__(self, service: base_service.BaseService, class_definitions=None):
        self.definition_dict = {}
        self.classes = {
            "NodeModel": NodeModel,
            "EdgeModel": EdgeModel
        }
        self.add(class_definitions)
        service.class_manager = self
        self.service = service

    def add(self, definition):
        if isinstance(definition, ClassDefinition):
            self.definition_dict[definition.class_name] = definition
        elif isinstance(definition, ClassDefinitionWrapper):
            self.definition_dict[definition.class_name] = definition.unpack()
        elif isinstance(definition, list):
            for each_dto in definition:
                self.add(each_dto)
        elif not definition:
            return
        else:
            raise Exception(f"unknown type for {definition}")

    def build(self):
        for name in self.definition_dict.keys():
            self.get(name)
        return self.classes

    def get(self, name):
        if name in self.classes:
            return self.classes[name]
        if name not in self.definition_dict:
            raise Exception(f"{name} does not exist in this class manager")
        definition = self.definition_dict[name]
        parent_classes = tuple(self.get(name) for name in definition.parent_classes)
        class_attributes = {
            **definition.class_attributes,
            "__init__": init_factory(definition.instance_properties, parent_classes)
        }
        self.classes[name] = type(name, parent_classes, class_attributes)
        return self.classes[name]
