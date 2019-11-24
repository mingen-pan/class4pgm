from class4pgm import Int, String
from class4pgm import NodeModel, EdgeModel


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

import redis
from class4pgm import RedisModelGraph

# connect to the local redis
r = redis.Redis()

# create a redis graph named example
model_graph = RedisModelGraph("example", r)

succeeded = model_graph.insert_defined_class([Person, Student, Teacher, Teach])

# [True, True, True, True]
print(succeeded)

model_graph = RedisModelGraph("example", r)
model_graph.add_node_model(john)
model_graph.add_node_model(kate)
model_graph.add_edge_model(teach)
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
Teach = model_graph.get_class('Teach')

# query every edges belonging to Teach class
edges = model_graph.match_edge(Teach(in_node=None, out_node=None))
for edge in edges:
    print(edge)
# ()-[:Teach]->()

model_graph.delete()
