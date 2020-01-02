import json

from class4pgm.edge_model import EdgeModel
from class4pgm.field import Field
from class4pgm.node_model import NodeModel
from class4pgm.service import ServiceGenerator


class ClassDefinition:
    primitive_types = {int, float, str, bool}
    collection_types = {list, tuple, dict}

    def __init__(self, class_name, parent_classes, class_attributes, instance_properties):
        self.class_name = class_name
        self.parent_classes = parent_classes
        self.class_attributes = class_attributes
        self.instance_properties = instance_properties

    def wrap(self):
        class_attributes = json.dumps(self.class_attributes)
        instance_properties = {
            key: Field.encode(value) for key, value in self.instance_properties.items()
        }
        instance_properties = json.dumps(instance_properties)
        return ClassDefinitionWrapper(self.class_name, self.parent_classes,
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
            elif type(value) in cls.collection_types:
                if cls.check_collection_type_value(value):
                    class_attributes[key] = value
            elif isinstance(value, Field):
                instance_properties[key] = value
        return cls(class_name=class_name, parent_classes=parent_classes, class_attributes=class_attributes,
                   instance_properties=instance_properties)

    @classmethod
    def check_collection_type_value(cls, value):
        if isinstance(value, list) or isinstance(value, tuple):
            for unit in value:
                if type(unit) in cls.primitive_types:
                    continue
                elif type(unit) in cls.collection_types:
                    if not cls.check_collection_type_value(unit):
                        return False
                else:
                    return False
            return True
        elif isinstance(value, dict):
            for k, v in value.items():
                if type(k) not in cls.primitive_types:
                    return False
                if type(v) in cls.primitive_types:
                    continue
                elif type(v) in cls.collection_types:
                    if not cls.check_collection_type_value(v):
                        return False
                else:
                    return False
            return True
        else:
            return False


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

    def __init__(self, class_name, parent_classes, class_attributes, instance_properties, **kwargs):
        self.class_name = class_name
        self.parent_classes = parent_classes
        self.class_attributes = class_attributes
        self.instance_properties = instance_properties
        self._attribute_check()
        super().__init__(**kwargs)

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
            except ValueError:
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
            except ValueError:
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
    A class to resolve and persist user-defined models. It will resolve class inheritance
    based on Depth-first Search. It uses lazy initialization to build dynamic classes. They are built
    only when you call `get` or `build`.

    Attributes
    _______
    classes: Dict[string]Type
        A dictionary used to query classes by their names.

    Methods
    -------
    __init__(self, service, class_definitions=None)
        construct a class_manager with a service that supports different graph databases.

    insert(self, definitions)
        insert one or a list of ClassDefinition instances

    build(self)
        build all the classes in this collection

    get(self, name)
        get the class with `name`. It will build this class and its parent classes automatically.
    """

    def __init__(self, graph):
        self.service = ServiceGenerator(graph)
        self.service.class_manager = self

        self.definition_dict = {}
        self.classes = {
            "NodeModel": NodeModel,
            "EdgeModel": EdgeModel,
            "ClassDefinitionWrapper": ClassDefinitionWrapper
        }
        self.fetch_class_definitions()
        self.build()

    def fetch_class_definitions(self):
        wrappers = self.service.fetch_class_definition_wrappers()
        self._insert(wrappers, upload=False)

    def insert_defined_class(self, defined_class, upload=True):
        if isinstance(defined_class, type):
            definition = ClassDefinition.resolve(defined_class)
            return self._insert([definition], upload=upload)[0]
        elif isinstance(defined_class, list):
            definitions = [ClassDefinition.resolve(element) for element in defined_class]
            return self._insert(definitions, upload=upload)

    def insert(self, definition, upload=True):
        if isinstance(definition, list):
            return self._insert(definition, upload=upload)
        else:
            return self._insert([definition], upload=upload)[0]

    def _insert(self, definitions: list, upload):
        if len(definitions) == 0:
            return []
        definitions = self._type_check_before_insert(definitions)
        results = [None] * len(definitions)
        for i, definition in enumerate(definitions):
            if definition is None:
                results[i] = False
                continue
            if upload:
                results[i] = self.service.upload_class_definition_wrapper(definition.wrap())
            else:
                results[i] = definition.class_name not in self.definition_dict
            # if a class has existed, then this class definition will not be inserted.
            if results[i]:
                self.definition_dict[definition.class_name] = definition
        return results

    def _type_check_before_insert(self, definitions: list):
        res = [None] * len(definitions)
        for i, definition in enumerate(definitions):
            if isinstance(definition, ClassDefinition):
                res[i] = definition
            elif isinstance(definition, ClassDefinitionWrapper):
                res[i] = definition.unpack()
        return res

    def delete(self, class_name, sync=True):
        if isinstance(class_name, list):
            self._delete(class_name, sync)
        else:
            self._delete([class_name], sync)

    def _delete(self, class_names: list, sync: bool):
        for class_name in class_names:
            self.classes.pop(class_name, None)
            if sync:
                self.service.delete_class_definition_wrapper(class_name)

    def build(self):
        for name in self.definition_dict.keys():
            self.get(name)
        return self.classes

    def get(self, name, ex=False):
        if name in self.classes:
            return self.classes[name]
        if name not in self.definition_dict:
            if ex:
                raise Exception(f"{name} does not exist in this class manager")
            return None
        definition = self.definition_dict[name]
        parent_classes = tuple(self.get(name) for name in definition.parent_classes)
        attributes = {
            **definition.class_attributes,
            **definition.instance_properties
        }
        self.classes[name] = type(name, parent_classes, attributes)
        return self.classes[name]

    def model_to_node(self, instance: NodeModel, auto_add=False):
        return self.service.model_to_node(instance, auto_add)

    def model_to_edge(self, instance: EdgeModel, auto_add=False):
        return self.service.model_to_edge(instance, auto_add=auto_add)

    def graph_to_models(self):
        return self.service.graph_to_models()

    def node_to_model(self, node):
        return self.service.node_to_model(node)

    def edge_to_model(self, edge):
        return self.service.edge_to_model(edge)
