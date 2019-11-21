import class4pgm
from class4pgm.edge import EdgeModel, Edge
from class4pgm.graph import Graph
from class4pgm.node import Node, NodeModel


class BaseService:

    def __init__(self, class_manager=None):
        self._class_manager = class_manager
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

    def to_node(self, instance: NodeModel):

        node = Node(alias=instance.get_alias(), labels=instance.get_labels(),
                    properties=instance.get_properties(), _id=instance.get_id())
        self.instance_to_node[instance] = node
        return node

    def to_edge(self, instance: EdgeModel):
        in_node = self.instance_to_node[instance._in_node]
        out_node = self.instance_to_node[instance._out_node]
        edge = Edge(in_node, instance.get_relationship(), out_node,
                    alias=instance.get_alias(), properties=instance.get_properties(), _id=instance.get_id())
        return edge

    def graph_to_models(self, graph: Graph, classes: dict):
        node_models = {}
        edge_models = {}
        for alias, node in graph.nodes.items():
            class_name = node.__class__.__name__
            if class_name not in classes:
                raise RuntimeError(f"{class_name} is not defined")
            node_models[alias] = self.to_node_model(node)

        for alias, edge in graph.edges.items():
            class_name = edge.__class__.__name__
            if class_name not in classes:
                raise RuntimeError(f"{class_name} is not defined")
            edge_models[alias] = self.to_edge_model(edge)

        return node_models, edge_models

    def to_node_model(self, node: Node):
        if len(node.labels) == 0 or node.labels[0] not in self._class_manager.classes:
            return None
        model_class = self._class_manager.classes[node.labels[0]]
        instance = model_class(_id=node.id, _alias=node.alias, **node.properties)
        self.node_to_instance[node] = instance
        return instance

    def to_edge_model(self, edge):
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
