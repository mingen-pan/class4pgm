from py2neo import Graph, Node, Relationship, NodeMatcher

import class4pgm
from class4pgm.edge_model import EdgeModel
from class4pgm.node_model import NodeModel
from class4pgm.service.base_service import BaseService


class Neo4jService(BaseService):

    def __init__(self, graph: Graph, class_manager=None):
        super().__init__(graph=graph, class_manager=class_manager)

    def model_to_node(self, instance: NodeModel, auto_add=False):
        node = Node(*instance.get_labels(), **instance.get_properties())
        self.model_to_node_dict[instance] = node
        if auto_add and self.graph:
            self.graph.create(node)
        return node

    def model_to_edge(self, instance: EdgeModel, auto_add=False):
        in_node = self.model_to_node_dict[instance.get_in_node()]
        out_node = self.model_to_node_dict[instance.get_out_node()]
        edge = Relationship(in_node, instance.get_relationship(), out_node, **instance.get_properties())
        if auto_add and self.graph:
            self.graph.create(edge)
        return edge

    def graph_to_models(self):
        pass

    def node_to_model(self, node: Node):
        if len(node.labels) == 0:
            return None
        T = self._class_manager.get(list(node.labels)[0])
        if not T:
            return None
        instance = T(_id=node.identity, **node)
        self.node_to_model_dict[node] = instance
        return instance

    def edge_to_model(self, edge: Relationship):
        T = self._class_manager.get(type(edge).__name__)
        if not T:
            return None

        if edge.start_node in self.node_to_model_dict:
            in_node = self.node_to_model_dict[edge.start_node]
        else:
            in_node = edge.start_node
        if edge.end_node in self.node_to_model_dict:
            out_node = self.node_to_model_dict[edge.end_node]
        else:
            out_node = edge.end_node

        return T(in_node=in_node, out_node=out_node, **edge)

    def upload_class_definition_wrapper(self, wrapper):
        if isinstance(wrapper, class4pgm.ClassDefinitionWrapper) and self.graph:
            node = self.model_to_node(wrapper)

            # Check if a class definition has already existed!
            matcher = NodeMatcher(self.graph).match("ClassDefinitionWrapper", class_name=wrapper.class_name)
            if len(matcher) > 0:
                return False

            self.graph.create(node)
            return True

    def delete_class_definition_wrapper(self, class_name):
        self.graph.run(f"Match (a:ClassDefinitionWrapper {{class_name: '{class_name}'}}) delete a")
        return True

    def fetch_class_definition_wrappers(self):
        if not self.graph:
            return []

        matcher = NodeMatcher(self.graph).match("ClassDefinitionWrapper")
        return [self.node_to_model(node) for node in list(matcher)]
