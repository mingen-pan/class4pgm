from class4pgm import NodeModel, EdgeModel
from class4pgm.field import String, List, Int, Bool


class Person(NodeModel):
    species = "human"
    name = String()
    age = Int()


class Student(Person):
    school = String()


class Teacher(Person):
    subject = String()


class IntlStudent(Student):
    country = String()


class Teach(EdgeModel):
    pass


test_a_definition_forms = [Person, Student, Teacher, IntlStudent, Teach]


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


test_b_definition_forms = [BioNode, Neuropil, Circuit, Species, FruitFly, Own]
