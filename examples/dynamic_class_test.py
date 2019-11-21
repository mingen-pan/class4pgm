from class4pgm.dynamic_class import ClassDefinitionWrapper, ClassManager, ClassDefinition
from class4pgm.field import String, Int, List
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


definitions = [
    ClassDefinition.resolve(Person),
    ClassDefinition.resolve(Student),
    ClassDefinition.resolve(Teacher),
    ClassDefinition.resolve(IntlStudent),
    ClassDefinition.resolve(Teach),
]

service = BaseService()
manager = ClassManager(service, definitions)
InstStudent = manager.get('IntlStudent')
Teacher = manager.get('Teacher')
Teach = manager.get('Teach')

tom = InstStudent(name="Tom", age=26, school='Foo School', country="No Country")
anne = Teacher(name="Anne", age=35, subject="Sleep Science")
teach = Teach(in_node=anne, out_node=tom)

print(tom)
print(service.to_node(tom))
print(anne)
print(teach)
print("\n\n\n", end='')

# exit(1)
# %% Integration test with Redis
import redis
import json

from class4pgm.field import String, Int, List, Bool
from class4pgm.dynamic_class import ClassManager, ClassDefinition
from class4pgm.field import String, Int, List
from class4pgm.node import NodeModel
from class4pgm.service.base_service import BaseService


# This creates a GraphArcana Graph class with the redisgraph Mixin


# This is the redis specific code that will be abstracted into a db connection API

class BioNode(NodeModel):
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


class Species(NodeModel):
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


class Own(EdgeModel):
    pass


definitions = [
    ClassDefinition.resolve(BioNode),
    ClassDefinition.resolve(Neuropil),
    ClassDefinition.resolve(Circuit),
    ClassDefinition.resolve(Species),
    ClassDefinition.resolve(FruitFly),
    ClassDefinition.resolve(Own),
]

service = BaseService()
manager = ClassManager(service, definitions)

Circuit = manager.get('Circuit')
FruitFly = manager.get('FruitFly')
Own = manager.get('Own')

fly = FruitFly(id="No. 1", sex='male', age=3, location='Mars', lived=True)
c = Circuit(name='circuit-1')
own = Own(in_node=fly, out_node=c)
print(fly)
print(own)
print(c)

n = manager.service.to_node(fly)
print(n)
fly = manager.service.to_node_model(n)
print(fly)

n = manager.service.to_node(c)
print(n)
c = manager.service.to_node_model(n)
print(c)

e = manager.service.to_edge(own)
print(e)
own = manager.service.to_edge_model(e)
print(own)
