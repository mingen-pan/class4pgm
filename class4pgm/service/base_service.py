from class4pgm.edge import EdgeModel, Edge
from class4pgm.node import Node, NodeModel


class BaseService:
    def to_node(self, instance):
        if isinstance(instance, NodeModel):
            return Node(**instance.convert())
        if isinstance(instance, Node):
            return instance
        return None

    def to_edge(self, instance):
        if isinstance(instance, EdgeModel):
            return Node(**instance.convert())
        if isinstance(instance, Edge):
            return instance
        return None

