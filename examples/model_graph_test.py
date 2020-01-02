import unittest

import redis

from class4pgm.model_graph.neo4j_model_graph import Neo4jModelGraph
from class4pgm.model_graph.redis_model_graph import RedisModelGraph
from examples.definition_forms import test_a_definition_forms


class ModelGraphTest(unittest.TestCase):
    def test_redis_model_graph(self):
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        graph = RedisModelGraph("test_redis_model_graph", r)
        graph.insert_defined_class(test_a_definition_forms)
        IntlStudent = graph.get_class("IntlStudent")
        Teacher = graph.get_class("Teacher")
        Teach = graph.get_class("Teach")

        tom = IntlStudent(name="Tom", age=26, school='Foo School', country="No Country")
        anne = Teacher(name="Anne", age=35, subject="Sleep Science")
        teach = Teach(in_node=anne, out_node=tom)

        graph.add_node_model(tom)
        graph.add_node_model(anne)
        graph.add_edge_model(teach)
        graph.commit()

        print('')
        # create a new graph to query
        graph = RedisModelGraph("test_redis_model_graph", self.r)
        results = graph.model_query("""Match (a) return a""")
        for result in results.result_set:
            print(result[0])

        edges = graph.match_edge(Teach(in_node=None, out_node=None))
        for edge in edges:
            print(edge)

        graph.delete()

    def test_neo4j_model_graph(self):
        uri = "bolt://localhost:7687"
        graph = Neo4jModelGraph(uri, auth=("neo4j", '123456'))
        graph.insert_defined_class(test_a_definition_forms)
        IntlStudent = graph.get_class("IntlStudent")
        Teacher = graph.get_class("Teacher")
        Teach = graph.get_class("Teach")

        tom = IntlStudent(name="Tom", age=26, school='Foo School', country="No Country")
        anne = Teacher(name="Anne", age=35, subject="Sleep Science")
        teach = Teach(in_node=anne, out_node=tom)

        graph.merge_node_model(tom)
        graph.merge_node_model(anne)
        graph.merge_edge_model(teach)

        print('')
        # create a new graph to query
        graph = Neo4jModelGraph(uri, auth=("neo4j", '123456'))
        cursor = graph.model_query("""Match (a) return a""")
        for record in cursor:
            print(record[0])

        edges = graph.match_edge(Teach(in_node=None, out_node=None))
        for edge in edges:
            print(edge)

        graph.delete_all()




if __name__ == '__main__':
    unittest.main()
