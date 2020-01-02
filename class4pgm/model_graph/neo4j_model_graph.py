from py2neo import Graph, NodeMatcher

from class4pgm.base_model import BaseModel
from class4pgm.class_definition import ClassManager
from class4pgm.edge_model import EdgeModel
from class4pgm.node_model import NodeModel


class Neo4jModelGraph(Graph):
    def __init__(self, uri=None, **settings):
        self.class_manager = ClassManager(self)

    def create_model(self, model: BaseModel):
        self.class_manager.model_to_db_object(model, auto_add=True)

    def create_node_model(self, node_model: NodeModel):
        self.class_manager.model_to_node(node_model, auto_add=True)

    def create_edge_model(self, edge_model: EdgeModel):
        """
        Addes an edge to the graph.
        """
        # Make sure edge both ends are in the graph
        self.class_manager.model_to_edge(edge_model, auto_add=True)

    def merge_node_model(self, node_model: NodeModel):
        node = self.class_manager.model_to_node(node_model)
        self.run(f"MERGE {node_model}")
        return node

    def merge_edge_model(self, edge_model: EdgeModel):
        """
        Addes an edge to the graph.
        """
        # Make sure edge both ends are in the graph
        edge = self.class_manager.model_to_edge(edge_model)
        in_node = edge_model.get_in_node()
        in_node.set_alias(None)
        out_node = edge_model.get_out_node()
        out_node.set_alias(None)
        edge_model.set_alias("edge_a")
        self.run(f"MATCH {in_node}, {out_node} MERGE {edge_model}")
        return edge

    def match_node(self, node_model: NodeModel):
        matcher = NodeMatcher(self).match(type(node_model).__name__, **node_model.get_properties())
        return list(matcher)

    def match_edge(self, edge_model: EdgeModel):
        if not edge_model.get_alias():
            edge_model._alias = 'edge_a'
        cursor = self.run(f"""Match {str(edge_model)} return {edge_model.get_alias()}""")
        return [record[0] for record in cursor]

    def model_query(self, q, parameters=None, **kwparameters):
        cursor = self.run(q, parameters=parameters, **kwparameters)
        model_result_set = []
        for record in cursor:
            model_row = []
            for element in record:
                try:
                    model_row.append(self.class_manager.db_object_to_model(element))
                except RuntimeError:
                    model_row.append(element)
            model_result_set.append(model_row)
        return model_result_set

    def get_class(self, class_name):
        return self.class_manager.get(class_name)

    def insert_defined_class(self, defined_class, upload=True):
        return self.class_manager.insert_defined_class(defined_class, upload=upload)

    def delete_defined_class(self, class_name, sync=True):
        return self.class_manager.delete(class_name, sync=sync)
