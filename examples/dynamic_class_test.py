import unittest

from class4pgm.class_definition import ClassManager, ClassDefinition
from class4pgm.service.base_element import Graph
from class4pgm.service.base_service import BaseService
from examples import definition_forms


class TestClassManager(unittest.TestCase):

    def test_basic_a(self):
        service = BaseService()
        manager = ClassManager(service)
        manager.add_raw_definition(definition_forms.test_a_definition_forms)
        InstStudent = manager.get('IntlStudent')
        Teacher = manager.get('Teacher')
        Teach = manager.get('Teach')

        tom = InstStudent(name="Tom", age=26, school='Foo School', country="No Country")
        anne = Teacher(name="Anne", age=35, subject="Sleep Science")
        teach = Teach(in_node=anne, out_node=tom)

        print(tom)
        print(service.model_to_node(tom))
        print(anne)
        print(teach)
        print("\n\n\n", end='')
        self.assertTrue(True)

    def test_basic_b(self):
        graph = Graph("test")
        service = BaseService(graph=graph)
        old_manager = ClassManager(service)
        old_manager.add_raw_definition(definition_forms.test_b_definition_forms)

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


if __name__ == '__main__':
    unittest.main()