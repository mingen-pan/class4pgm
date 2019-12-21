from redisgraph import Node, Graph, Edge

import class4pgm
from class4pgm import NodeModel, EdgeModel
from class4pgm.service.base_service import BaseService


class RedisGraphService(BaseService):

    def __init__(self, redis_graph: Graph, class_manager=None):
        self.redis_graph = redis_graph
        super().__init__(class_manager=class_manager)

    def model_to_node(self, instance: NodeModel, auto_add=False):
        node = Node(alias=instance.get_alias(), label=instance.get_labels()[0],
                    properties=instance.get_properties(), node_id=instance.get_id())
        self.model_to_node_dict[instance] = node
        if auto_add and self.redis_graph:
            self.redis_graph.add_node(node)
        return node

    def model_to_edge(self, instance: EdgeModel, auto_add=False):
        in_node = self.model_to_node_dict[instance.get_in_node()]
        out_node = self.model_to_node_dict[instance.get_out_node()]
        edge = Edge(in_node, instance.get_relationship(), out_node, properties=instance.get_properties())
        if auto_add and self.redis_graph:
            self.redis_graph.add_edge(edge)
        return edge

    def graph_to_models(self):
        node_models = {}
        edge_models = {}
        for alias, node in self.redis_graph.nodes.items():
            node_models[alias] = self.node_to_model(node)

        for alias, edge in self.redis_graph.edges.items():
            edge_models[alias] = self.edge_to_model(edge)

        return node_models, edge_models

    def node_to_model(self, node: Node):
        if not node.label:
            return None
        model_class = self._class_manager.get(node.label)
        if not model_class:
            return None
        instance = model_class(_id=node.id, _alias=node.alias, **node.properties)
        self.node_to_model_dict[id(node)] = instance
        return instance

    def edge_to_model(self, edge: Edge):
        model_class = self._class_manager.get(edge.relation)
        if not model_class:
            return None

        if id(edge.src_node) in self.node_to_model_dict:
            in_node = self.node_to_model_dict[id(edge.src_node)]
        else:
            in_node = edge.src_node
        if id(edge.dest_node) in self.node_to_model_dict:
            out_node = self.node_to_model_dict[id(edge.dest_node)]
        else:
            out_node = edge.dest_node

        return model_class(in_node=in_node, out_node=out_node, **edge.properties)

    def upload_class_definition_wrapper(self, wrapper):
        if isinstance(wrapper, class4pgm.ClassDefinitionWrapper) and self.redis_graph:
            wrapper.class_attributes = wrapper.class_attributes.replace('"', '\\"')
            wrapper.instance_properties = wrapper.instance_properties.replace('"', '\\"')
            node = self.model_to_node(wrapper)

            # Check if a class definition has already existed!
            node.alias = "a"
            result = self.redis_graph.query(f"Match ({node.alias}:ClassDefinitionWrapper "
                                            f"{{class_name: \"{wrapper.class_name}\"}}) "
                                            f"return count({node.alias}) as cnt")
            if result.result_set and result.result_set[0][0] > 0:
                return False

            self.redis_graph.add_node(node)
            self.redis_graph.flush()
            return True

    def delete_class_definition_wrapper(self, class_name):
        result = self.redis_graph.query(f"Match (a:ClassDefinitionWrapper {{class_name: '{class_name}'}}) delete a")
        return result.nodes_deleted > 0

    def fetch_class_definition_wrappers(self):
        if not self.redis_graph:
            return []
        q_str = """Match (p:ClassDefinitionWrapper) return p"""
        results = self.redis_graph.query(q_str)
        if len(results.result_set) == 0:
            return []
        nodes = [row[0] for row in results.result_set]
        return [self.node_to_model(node) for node in nodes]
