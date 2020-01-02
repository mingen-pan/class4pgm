from py2neo import Graph, NodeMatcher, RelationshipMatcher, Node, Relationship

from class4pgm.class_definition import ClassManager
from class4pgm.edge_model import EdgeModel
from class4pgm.node_model import NodeModel
from class4pgm.service.neo4j_service import Neo4jService


class Neo4jModelGraph(Graph):
    def __init__(self):
        super().__init__()
        self.service = Neo4jService(self)
        self.class_manager = ClassManager(self.service)

    def create_node_model(self, node_model: NodeModel):
        self.service.model_to_node(node_model, auto_add=True)

    def create_edge_model(self, edge_model: EdgeModel):
        """
        Addes an edge to the graph.
        """
        # Make sure edge both ends are in the graph
        self.service.model_to_edge(edge_model, auto_add=True)

    def merge_node_model(self, node_model: NodeModel):
        node = self.service.model_to_node(node_model)
        self.merge(node)

    def merge_edge_model(self, edge_model: EdgeModel):
        """
        Addes an edge to the graph.
        """
        # Make sure edge both ends are in the graph
        edge = self.service.model_to_edge(edge_model)
        self.merge(edge)

    def match_node(self, node_model: NodeModel):
        matcher = NodeMatcher(self).match(type(node_model).__name__, **node_model.get_properties())
        return list(matcher)

    def match_edge(self, edge_model: EdgeModel):
        matcher = RelationshipMatcher(self).match(type(edge_model).__name__, **edge_model.get_properties())
        return list(matcher)

    def model_query(self, q, parameters=None, **kwparameters):
        cursor = self.run(q, parameters=parameters, **kwparameters)
        model_result_set = []
        for record in cursor:
            model_row = []
            for element in record:
                if isinstance(element, Node):
                    model_row.append(self.service.node_to_model(element))
                elif isinstance(element, Relationship):
                    model_row.append(self.service.edge_to_model(element))
                else:
                    model_row.append(element)
            model_result_set.append(model_row)
        return model_result_set

    def get_class(self, class_name):
        return self.class_manager.get(class_name)

    def insert_defined_class(self, defined_class, upload=True):
        return self.class_manager.insert_defined_class(defined_class, upload=upload)

    def delete_defined_class(self, class_name, sync=True):
        return self.class_manager.delete(class_name, sync=sync)
