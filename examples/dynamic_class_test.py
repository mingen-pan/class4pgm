from class4pgm.dynamic_class import DynamicClassDto, ClassCollection
from class4pgm.field import String, Int
from class4pgm.node import NodeModel
from class4pgm.edge import EdgeModel
from class4pgm.service.base_service import BaseService



class Person(NodeModel):
    species = "animal"
    name = String(unique=True)
    age = Int()


class Student(Person):
    school = String()


class Teacher(Person):
    subject = String()


class IntlStudent(Student, Teacher):
    country = String(nullable=False)


class Teach(EdgeModel):
    pass


dto_list = [
    DynamicClassDto.load(Person),
    DynamicClassDto.load(Student),
    DynamicClassDto.load(Teacher),
    DynamicClassDto.load(IntlStudent),
    DynamicClassDto.load(Teach),
]

service = BaseService()
collection = ClassCollection(dto_list)
InstStudent = collection.get('IntlStudent')
Teacher = collection.get('Teacher')
Teach = collection.get('Teach')

tom = InstStudent(name="Tom", age=26, school='Foo School', country="No Country")
anne = Teacher(name="Anne", age=35, subject="Sleep Science")
teach = Teach(in_node=anne, out_node=tom)

print(tom)
print(service.to_node(tom))
print(anne)
print(teach)
print("\n\n\n", end='')

exit(1)
# %% Integration test with Redis
import redis
import json

from grapharcana.dialects.redisgraph.mixin import Mixin
from grapharcana.ogm.graph import Graph
from grapharcana.dialects.query import Query


# This creates a GraphArcana Graph class with the redisgraph Mixin
class ClassGraph(Mixin, Graph):
    def __init__(self, *args):
        super().__init__(*args)


# This is the redis specific code that will be abstracted into a db connection API
db = redis.Redis(host='localhost', port=6379, decode_responses=True)
arcana = ClassGraph('classes', db)


class BioNode(Vertex):
    element_type = 'BioNode'
    element_plural = 'BioNodes'


class Neuropil(BioNode):
    element_type = 'Neuropil'
    element_plural = 'Neuropils'
    name = String(nullable=False, unique=False)
    synonyms = List(nullable=True, unique=False)


class Circuit(BioNode):
    element_type = 'Circuit'
    element_plural = 'Circuits'
    name = String(nullable=False, unique=False)


class Species(Vertex):
    element_type = 'Species'
    element_plural = 'Species'


class FruitFly(Species):
    element_type = 'Fruit fly'
    element_plural = 'Fruit flies'
    id = String()
    sex = String()
    age = Int()
    location = String()
    lived = Bool()


dto_list = [
    DynamicClassDto.load(BioNode),
    DynamicClassDto.load(Neuropil),
    DynamicClassDto.load(Circuit),
    DynamicClassDto.load(Species),
    DynamicClassDto.load(FruitFly),
]

for dto in dto_list:
    arcana.create(DynamicClassDto, **dto.properties())

class_filter = Query()
class_filter.MATCH(DynamicClassDto, True)
print(class_filter)

query_result = arcana.all(class_filter)
dto_list = [result[0] for result in query_result]
collection = ClassCollection(dto_list)
Circuit = collection.get('Circuit')
FruitFly = collection.get('FruitFly')

c = Circuit(name='circuit-1')
print(c.properties())
fly = FruitFly(id="No. 1", sex='male', age=3, location='Mars', lived=True)
print(fly.properties())
arcana.delete()

