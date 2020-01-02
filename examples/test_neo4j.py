import unittest

from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher

from class4pgm import ClassManager
from examples import definition_forms


class TestNeo4j(unittest.TestCase):

    def setUp(self) -> None:
        uri = "bolt://localhost:7687"
        self.graph = Graph(uri, auth=("neo4j", '123456'))

    def test_basic(self):
        a = Node("Person", name="Peter")
        b = Node("Person", name="Jack")
        Knows = Relationship.type("Knows")
        self.graph.create(a | b)
        self.graph.create(Knows(a, b))
        cursor = self.graph.run("Match (a) return a")
        for record in cursor:
            print(record)

        cursor = self.graph.run("Match ()-[a]->() return a")
        for record in cursor:
            print(record)
        self.graph.delete_all()

    def test_on_neo4j_graph(self):
        old_manager = ClassManager(self.graph)
        old_manager.insert_defined_class(definition_forms.test_a_definition_forms)

        # get all the classes
        IntlStudent = old_manager.get("IntlStudent")
        Teacher = old_manager.get("Teacher")
        Teach = old_manager.get("Teach")
        print(Teacher.code)
        self.assertEqual(Teacher.code[0][2], 'a')
        self.assertEqual(Teacher.code[1]['banana'], 123)

        john = IntlStudent(name="John", age=23, school="Columbia", country="No country")
        kate = Teacher(name="Kate", age=18, subject="Computer Science")
        teach = Teach(in_node=kate, out_node=john)

        old_manager.service.model_to_node(john, auto_add=True)
        old_manager.service.model_to_node(kate, auto_add=True)
        old_manager.service.model_to_edge(teach, auto_add=True)

        self.setUp()
        manager = ClassManager(self.graph)

        matcher = NodeMatcher(self.graph).match()
        models = [manager.node_to_model(node) for node in list(matcher)]
        for model in models:
            print(model)

        matcher = RelationshipMatcher(self.graph).match()
        models = [manager.edge_to_model(edge) for edge in list(matcher)]
        for model in models:
            print(model)

        self.graph.delete_all()

    def test_duplicate_upload_class(self):
        manager = ClassManager(self.graph)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)

        results = list(NodeMatcher(self.graph).match("ClassDefinitionWrapper"))
        for result in results:
            print(result)
        self.assertEqual(len(results), len(definition_forms.test_a_definition_forms))
        self.graph.delete_all()

    def test_delete_class(self):
        manager = ClassManager(self.graph)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)
        manager.delete([raw_definition.__name__ for raw_definition in definition_forms.test_a_definition_forms])
        result = NodeMatcher(self.graph).match("ClassDefinitionWrapper")
        self.assertEqual(len(result), 0)
        self.graph.delete_all()
