import unittest

import redis
import redisgraph

import class4pgm.service.base_element as base_element
from class4pgm.class_definition import ClassManager
from class4pgm.service.base_service import BaseService
from class4pgm.service.redis_graph_service import RedisGraphService
from examples import definition_forms


class TestClassManager(unittest.TestCase):
    def setUp(self) -> None:
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def test_basic_a(self):
        tom = definition_forms.IntlStudent(name="Tom", age=26, school='Foo School', country="No Country")
        anne = definition_forms.Teacher(name="Anne", age=35, subject="Sleep Science")
        teach = definition_forms.Teach(in_node=anne, out_node=tom)
        print(tom)
        print(anne)
        print(teach)
        self.assertTrue(True)

    def test_basic_b(self):
        graph = base_element.Graph("test")
        service = BaseService(graph=graph)
        old_manager = ClassManager(service)
        old_manager.insert_defined_class(definition_forms.test_b_definition_forms)

        manager = ClassManager(service)

        Circuit = manager.get('Circuit')
        FruitFly = manager.get('FruitFly')
        Own = manager.get('Own')

        fly = FruitFly(id="No. 1", sex='male', age=3, location='Mars', lived=True)
        c = Circuit(name='circuit-1')
        own = Own(in_node=fly, out_node=c)
        print(fly)
        print(own)
        print(c)

        n = manager.service.model_to_node(fly)
        print(n)
        fly = manager.service.node_to_model(n)
        print(fly)

        n = manager.service.model_to_node(c)
        print(n)
        c = manager.service.node_to_model(n)
        print(c)

        e = manager.service.model_to_edge(own)
        print(e)
        own = manager.service.edge_to_model(e)
        print(own)

    def test_on_redis_graph(self):
        redis_graph = redisgraph.Graph('school', self.r)
        service = RedisGraphService(redis_graph=redis_graph)
        old_manager = ClassManager(service)
        old_manager.insert_defined_class(definition_forms.test_a_definition_forms)

        # get all the classes
        IntlStudent = old_manager.get("IntlStudent")
        Teacher = old_manager.get("Teacher")
        Teach = old_manager.get("Teach")

        john = IntlStudent(name="John", age=23, school="Columbia", country="No country")
        kate = Teacher(name="Kate", age=18, subject="Computer Science")
        teach = Teach(in_node=kate, out_node=john)

        old_manager.service.model_to_node(john, auto_add=True)
        old_manager.service.model_to_node(kate, auto_add=True)
        old_manager.service.model_to_edge(teach, auto_add=True)
        redis_graph.flush()

        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        redis_graph = redisgraph.Graph('school', r)
        service = RedisGraphService(redis_graph=redis_graph)
        manager = ClassManager(service)

        results = redis_graph.query("""Match (p) return p""")
        nodes = [row[0] for row in results.result_set]
        models = [service.node_to_model(node) for node in nodes]
        for model in models:
            print(model)

        results = redis_graph.query("""Match ()-[a]->() return a""")
        edges = [row[0] for row in results.result_set]
        models = [service.edge_to_model(edge) for edge in edges]
        for model in models:
            print(model)

        redis_graph.delete()

    def test_duplicate_upload_class(self):
        redis_graph = redisgraph.Graph('duplicate_upload_class', self.r)
        service = RedisGraphService(redis_graph=redis_graph)
        manager = ClassManager(service)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)
        result = redis_graph.query("""Match (a:ClassDefinitionWrapper) return count(a) as cnt""")
        self.assertEqual(result.result_set[0][0], len(definition_forms.test_a_definition_forms))
        redis_graph.delete()

if __name__ == '__main__':
    unittest.main()