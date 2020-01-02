from redisgraph import Graph

from class4pgm.base_model import BaseModel
from class4pgm.class_definition import ClassManager
from class4pgm.edge_model import EdgeModel
from class4pgm.node_model import NodeModel


class RedisModelGraph(Graph):
    def __init__(self, name, redis_conn):
        super().__init__(name, redis_conn)
        self.class_manager = ClassManager(self)

    def add_model(self, model: BaseModel):
        self.class_manager.model_to_db_object(model, auto_add=True)

    def add_node_model(self, node_model: NodeModel):
        self.class_manager.model_to_node(node_model, auto_add=True)

    def add_edge_model(self, edge_model: EdgeModel):
        """
        Addes an edge to the graph.
        """
        # Make sure edge both ends are in the graph
        self.class_manager.model_to_edge(edge_model, auto_add=True)

    def match_node(self, node_model: NodeModel):
        if not node_model.get_alias():
            node_model._alias = 'a'
        result = self.model_query(f"""Match {str(node_model)} return {node_model.get_alias()}""")
        return [row[0] for row in result.result_set]

    def match_edge(self, edge_model: EdgeModel):
        if not edge_model.get_alias():
            edge_model._alias = 'a'
        result = self.model_query(f"""Match {str(edge_model)} return {edge_model.get_alias()}""")
        return [row[0] for row in result.result_set]

    def model_query(self, q, params=None):
        result = self.query(q, params)
        model_result_set = []
        for row in result.result_set:
            model_row = []
            for element in row:
                try:
                    model_row.append(self.class_manager.db_object_to_model(element))
                except RuntimeError:
                    model_row.append(element)
            model_result_set.append(model_row)
        result.result_set = model_result_set
        return result

    def get_class(self, class_name):
        return self.class_manager.get(class_name)

    def insert_defined_class(self, defined_class, upload=True):
        return self.class_manager.insert_defined_class(defined_class, upload=upload)

    def delete_defined_class(self, class_name, sync=True):
        return self.class_manager.delete(class_name, sync=sync)
