# class4pgm
`class4pgm` is a library to define and persist classes of the nodes and edges of property graph models (e.g., RedisGraph and Neo4j). The definition of a class is concise and follows the convention used by other ogm libs (e.g., `py2neo`). However, this library also allows users to persist their defined classes in graph databases, so that different clients can share their defined class schema. `class4pgm` is graph-database independent, and current supports for `RedisGraph` and `Neo4j`. One can always convert the instances of their defined classes into the nodes and edges compatible with `Cypher`, a generally graph query language used by multiple graph databases.


Here is an example how one can use `class4pgm` to define and persist classes.

First, Let's import the lib.

```
from class4pgm import NodeModel, EdgeModel
from class4pgm import Int, String, Bool, Float
```

We will inherit `NodeModel` and `EdgeModel` to define our classes for nodes and edges. Datatypes like `Int` will be used to represent the field of our defined classes. Let's first define a few classes and construct some instances.

```
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
teach = Teach(in_node=kate, out_node=john)

print(tom)
print(teach)
```

We have defined these classes locally, and now need to persist them in the graph database.

```
import redis
from class4pgm import RedisModelGraph

# connect to the local redis
r = redis.Redis()

# create a redis graph named example
model_graph = RedisModelGraph("example", r)

succeeded = model_graph.insert_defined_class([Person, Student, Teacher, Teach])

#[True, True, True, True]
print(succeeded)
```
`succeeded` returned from `model_graph.insert_defined_class([...])` indicates whether the classes are persisted successfully. `True` means a class succuessfully persisted, otherwise not. The failure to presist a class may be due to that another class defintion will the same class name has already been persisted.

Now also insert some nodes and edges into the graph database.

```
model_graph = RedisModelGraph("example", r)
model_graph.add_node_model(john)
model_graph.add_node_model(kate)
model_graph.add_edge_model(teach)
model_graph.flush()
```

Now both the instances of our defined classes and the class definitions are persisted succuessfully. Let's try to retrieve them back from the graph database. 

```
#open a new client to the graph database

r = redis.Redis()
#the defined classes will be retrieved automatically during the construction of the graph client.
model_graph = RedisModelGraph("example", r)

#retrieve every nodes
results = model_graph.model_query("""Match (a) return a""")
for result in results.result_set:
    print(result[0])
    
# (:ClassDefinitionWrapper {...})
# ...
# (:Student:Person {school:"Columbia U",name:"John",age:23})
# (:Teacher:Person {subject:"Computer Science",name:"Kate",age:30})
    

#acquire Teach class.
Teach = model_graph.get_class('Teach')

#query every edges belonging to Teach class
edges = model_graph.match_edge(Teach(in_node=None, out_node=None))
for edge in edges:
    print(edge)
# ()-[:Teach]->()

graph.delete()


```



