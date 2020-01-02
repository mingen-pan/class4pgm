import class4pgm
from class4pgm.edge_model import EdgeModel
from class4pgm.node_model import NodeModel
from class4pgm.service.base_element import Node, Edge


class BaseService:

    def __init__(self, graph=None, class_manager=None):
        self.graph = graph
        self._class_manager = class_manager
        self.model_to_node_dict = {}
        self.node_to_model_dict = {}

    def clear(self):
        self.model_to_node_dict = {}
        self.node_to_model_dict = {}

    @property
    def class_manager(self):
        return self._class_manager

    @class_manager.setter
    def class_manager(self, val):
        assert type(val) is class4pgm.ClassManager
        self._class_manager = val

    def model_to_node(self, instance: NodeModel, auto_add=False):
        node = Node(alias=instance.get_alias(), labels=instance.get_labels(),
                    properties=instance.get_properties(), _id=instance.get_id())
        self.model_to_node_dict[instance] = node
        if auto_add and self.graph:
            self.graph.add_node(node)
        return node

    def model_to_edge(self, instance: EdgeModel, auto_add=False):
        assert instance.get_in_node() in self.model_to_node_dict and \
               instance.get_out_node() in self.model_to_node_dict

        in_node = self.model_to_node_dict[instance.get_in_node()]
        out_node = self.model_to_node_dict[instance.get_out_node()]
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
        if not isinstance(node.labels, list) or len(node.labels) == 0:
            return None
        model_class = self._class_manager.get(node.labels[0])
        if not model_class:
            return None
        instance = model_class(_id=node.id, _alias=node.alias, **node.properties)
        self.node_to_model_dict[node] = instance
        return instance

    def edge_to_model(self, edge: Edge):
        model_class = self._class_manager.get(edge.relationship)
        if not model_class:
            return None

        if edge.in_node in self.node_to_model_dict:
            in_node = self.node_to_model_dict[edge.in_node]
        else:
            in_node = edge.in_node
        if edge.out_node in self.node_to_model_dict:
            out_node = self.node_to_model_dict[edge.out_node]
        else:
            out_node = edge.out_node

        return model_class(in_node=in_node, out_node=out_node, _id=edge.id, _alias=edge.alias, **edge.properties)

    def upload_class_definition_wrapper(self, wrapper):
        if isinstance(wrapper, class4pgm.ClassDefinitionWrapper) and self.graph:
            node = self.model_to_node(wrapper)
            return self.graph.add_class_definition(node)
        return False

    def delete_class_definition_wrapper(self, class_name):
        return self.graph.delete_class_definition(class_name)

    def fetch_class_definition_wrappers(self):
        if self.graph:
            nodes = self.graph.class_definitions.values()
            return [self.node_to_model(node) for node in nodes]
        return []
