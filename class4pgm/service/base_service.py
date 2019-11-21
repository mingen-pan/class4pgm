import class4pgm
from class4pgm import NodeModel, EdgeModel
from class4pgm.service.base_element import Node, Edge, Graph


class BaseService:

    def __init__(self, graph: Graph = None, class_manager=None):
        self.graph = graph
        self._class_manager = class_manager
        self.instance_to_node = {}
        self.node_to_instance = {}

    def clear(self):
        self.instance_to_node = {}
        self.node_to_instance = {}

    @property
    def class_manager(self):
        return self._class_manager

    @class_manager.setter
    def class_manager(self, val):
        if not val:
            assert type(val) is class4pgm.ClassManager
        self._class_manager = val

    def model_to_node(self, instance: NodeModel, auto_add=False):

        node = Node(alias=instance.get_alias(), labels=instance.get_labels(),
                    properties=instance.get_properties(), _id=instance.get_id())
        self.instance_to_node[instance] = node
        if auto_add and self.graph:
            self.graph.add_node(node)
        return node

    def model_to_edge(self, instance: EdgeModel, auto_add=False):
        in_node = self.instance_to_node[instance.get_in_node()]
        out_node = self.instance_to_node[instance.get_out_node()]
        edge = Edge(in_node, instance.get_relationship(), out_node,
                    alias=instance.get_alias(), properties=instance.get_properties(), _id=instance.get_id())
        if auto_add and self.graph:
            self.graph.add_edge(edge)
        return edge

    def graph_to_models(self):
        node_models = {}
        edge_models = {}
        for alias, node in self.graph.nodes.items():
            node_models[alias] = self.node_to_model(node)

        for alias, edge in self.graph.edges.items():
            edge_models[alias] = self.edge_to_model(edge)

        return node_models, edge_models

    def node_to_model(self, node: Node):
        if len(node.labels) == 0 or node.labels[0] not in self._class_manager.classes:
            return None
        model_class = self._class_manager.classes[node.labels[0]]
        instance = model_class(_id=node.id, _alias=node.alias, **node.properties)
        self.node_to_instance[node] = instance
        return instance

    def edge_to_model(self, edge):
        if edge.relationship not in self._class_manager.classes:
            return None

        if edge.in_node in self.node_to_instance:
            in_node = self.node_to_instance[edge.in_node]
        else:
            in_node = edge.in_node
        if edge.out_node in self.node_to_instance:
            out_node = self.node_to_instance[edge.out_node]
        else:
            out_node = edge.out_node

        model_class = self._class_manager.classes[edge.relationship]
        return model_class(in_node=in_node, out_node=out_node, _id=edge.id, _alias=edge.alias, **edge.properties)

    def upload_class_definition_wrapper(self, wrapper):
        if isinstance(wrapper, class4pgm.ClassDefinitionWrapper) and self.graph:
            wrapper = self.model_to_node(wrapper)
            self.graph.add_class_definition(wrapper)

    def fetch_class_definition_wrappers(self):
        if self.graph:
            nodes = self.graph.class_defintions.values()
            wrappers = [self.node_to_model(node) for node in nodes]
            return wrappers
