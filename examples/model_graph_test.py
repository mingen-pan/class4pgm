import unittest

import redis

from class4pgm.model_graph.redis_model_graph import RedisModelGraph
from examples.definition_forms import test_a_definition_forms


class ModelGraphTest(unittest.TestCase):
    def setUp(self) -> None:
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def test_redis_model_graph(self):
        graph = RedisModelGraph("test_redis_model_graph", self.r)
        graph.insert_raw_definition(test_a_definition_forms)
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

        results = graph.match_edge(Teach(in_node=None, out_node=None))
        for result in results.result_set:
            print(result[0])

        graph.delete()


if __name__ == '__main__':
    unittest.main()
