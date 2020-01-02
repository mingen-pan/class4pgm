from class4pgm import NodeModel, EdgeModel
from class4pgm.field import Int, String


class Person(NodeModel):
    species = "human"
    name = String()
    age = Int()


class Student(Person):
    school = String()


class Teacher(Person):
    subject = String()


class Teach(EdgeModel):
    pass


tom = Person(name="Tom", age=15)
john = Student(name='John', age=23, school="Columbia U")
kate = Teacher(name='Kate', age=30, subject="Computer Science")
teach = Teach(in_node=kate, out_node=john, role="full time")

print(tom)
print(teach)


def introduction_1():
    import redis
    from class4pgm import RedisModelGraph

    # connect to the local redis
    r = redis.Redis()

    # create a redis graph named example
    model_graph = RedisModelGraph("example", r)

    succeeded = model_graph.insert_defined_class([Person, Student, Teacher, Teach])

    # [True, True, True, True]
    print(succeeded)

    model_graph.add_model(john)
    model_graph.add_model(kate)
    model_graph.add_model(teach)
    model_graph.flush()

    """
        Open new client to retrieve classes and instances.
    """

    r = redis.Redis()
    # the defined classes will be retrieved automatically during the construction of the graph client.
    model_graph = RedisModelGraph("example", r)

    # retrieve every nodes
    results = model_graph.model_query("""Match (a) return a""")
    for result in results.result_set:
        print(result[0])

    # (:ClassDefinitionWrapper {...})
    # ...
    # (:IntlStudent:Student:Person)
    # (:Teacher:Person)

    # acquire Teach class.
    T = model_graph.get_class('Teach')

    # query every edges belonging to Teach class
    edges = model_graph.match_edge(T(in_node=None, out_node=None))
    for edge in edges:
        print(edge)
    # ()-[:Teach]->()

    model_graph.delete()


def introduction_2():
    import redis
    from redisgraph import Graph
    from class4pgm import ClassManager

    # connect to the local redis
    r = redis.Redis()
    # create a redis graph named example
    graph = Graph("example", r)

    manager = ClassManager(graph)
    succeeded = manager.insert_defined_class([Person, Student, Teacher, Teach])
    # [True, True, True, True]
    print(succeeded)

    manager.model_to_db_object(john, auto_add=True)
    manager.model_to_db_object(kate, auto_add=True)
    manager.model_to_db_object(teach, auto_add=True)
    graph.flush()

    """
        Open new client to retrieve classes and instances.
    """

    r = redis.Redis()
    # the defined classes will be retrieved automatically during the construction of the graph client.
    manager = ClassManager(graph)

    # retrieve every nodes
    results = graph.query("""Match (a) return a""")
    for result in results.result_set:
        print(manager.db_object_to_model(result[0]))

    # (:ClassDefinitionWrapper {...})
    # ...
    # (:IntlStudent:Student:Person)
    # (:Teacher:Person)

    # acquire Teach class.
    T = manager.get('Teach')

    # query every edges belonging to Teach class
    result = graph.query(f"Match ()-[a:{Teach.__name__}]->() return a")
    for row in result.result_set:
        print(manager.edge_to_model(row[0]))
    # ()-[:Teach]->()

    graph.delete()


if __name__ == '__main__':
    introduction_1()
    introduction_2()
