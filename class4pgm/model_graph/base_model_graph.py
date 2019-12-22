from class4pgm.class_definition import ClassManager
from class4pgm.edge_model import EdgeModel
from class4pgm.node_model import NodeModel
from class4pgm.service.base_element import Graph
from class4pgm.service.base_service import BaseService


class BaseModelGraph(Graph):
    def __init__(self, name):
        super().__init__(name)
        self.service = BaseService(self)
        self.class_manager = ClassManager(self.service)

    def add_node(self, model: NodeModel):
        self.service.model_to_node(model, auto_add=True)

    def add_edge(self, model: EdgeModel):
        """
        Addes an edge to the graph.
        """
        # Make sure edge both ends are in the graph
        self.service.model_to_edge(model, auto_add=True)

    def get_class(self, class_name):
        return self.class_manager.get(class_name)

    def insert_defined_class(self, raw_definitions, upload=True):
        return self.class_manager.insert_defined_class(raw_definitions, upload=upload)

    def delete_defined_class(self, class_names, sync=True):
        return self.class_manager.delete(class_names, sync=sync)
