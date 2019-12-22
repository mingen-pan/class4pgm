import unittest

from py2neo import Graph, Node, Relationship, NodeMatcher

from class4pgm import ClassManager
from class4pgm.service.neo4j_service import Neo4jService
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

    def test_duplicate_upload_class(self):
        service = Neo4jService(self.graph)
        manager = ClassManager(service)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)

        result = NodeMatcher(self.graph).match("ClassDefinitionWrapper")
        self.assertEqual(len(result), len(definition_forms.test_a_definition_forms))
        self.graph.delete_all()

    def test_delete_class(self):
        service = Neo4jService(self.graph)
        manager = ClassManager(service)
        manager.insert_defined_class(definition_forms.test_a_definition_forms)
        manager.delete([raw_definition.__name__ for raw_definition in definition_forms.test_a_definition_forms])
        result = NodeMatcher(self.graph).match("ClassDefinitionWrapper")
        self.assertEqual(len(result), 0)
        self.graph.delete_all()
