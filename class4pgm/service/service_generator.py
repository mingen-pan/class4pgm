from py2neo import Graph as Neo4jGraph
from redisgraph import Graph as RedisGraph

from class4pgm.service.base_element import Graph as BaseGraph
from class4pgm.service.base_service import BaseService
from class4pgm.service.neo4j_service import Neo4jService
from class4pgm.service.redis_graph_service import RedisGraphService


class ServiceGenerator:

    def __new__(cls, graph):
        if isinstance(graph, RedisGraph):
            return RedisGraphService(graph)

        elif isinstance(graph, Neo4jGraph):
            return Neo4jService(graph)

        elif isinstance(graph, BaseGraph):
            return BaseService(graph)

        else:
            raise RuntimeError("Unknown Graph to initialize")
