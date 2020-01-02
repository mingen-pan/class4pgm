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

Here is the example of using `RedisGraph`.
```
import redis
from redisgraph import Graph as RedisGraph
from class4pgm import ClassManager

# connect to the local redis
r = redis.Redis()
# connect to the local redisgraph named example
graph = RedisGraph("example", r)

# create a class manager for this graph
manager = ClassManager(graph)

succeeded = manager.insert_defined_class([Person, Student, Teacher, Teach])

#[True, True, True, True]
print(succeeded)
```
`succeeded` returned from `manager.insert_defined_class([...])` indicates whether the classes are persisted successfully. `True` means a class succuessfully persisted, otherwise not. The failure to presist a class may be due to that another class defintion will the same class name has already been persisted.

If you prefer to use `Neo4j`, we just need to change a bit of code:
```
from py2neo import Graph as NeoGraph

uri = "bolt://localhost:7687"
graph = NeoGraph(uri, auth=("neo4j", 'your_password'))

# create the class manager for your graph database
manager = ClassManager(graph)
```

`ClassManager` provides the same APIs for every graph database, so the following example should work on both `Neo4j` and `RedisGraph`. Now the continuing demonstration will be based on `RedisGraph`.

Now insert some nodes and edges into the graph database.
```
# manager = ClassManager(graph)
manager.model_to_db_object(john, auto_add=True)
manager.model_to_db_object(kate, auto_add=True)
manager.model_to_db_object(teach, auto_add=True)

# the db_object (nodes and edges) are only stored in the cache of RedisGraph, 
# and we have to flush them.
graph.flush()
```

Now both the instances of our defined classes and the class definitions are persisted successfully. Let's try to retrieve them back from the graph database. 

```
#open a new client to the graph database
r = redis.Redis()
graph = RedisGraph("example", r)

#the defined classes will be retrieved automatically during the construction of the graph client.
manager = ClassManager(graph)

#retrieve every nodes using the original RedisGraph client
results = graph.query("""Match (a) return a""")
for result in results.result_set:
    # we convert the RedisGraph objects to the model objects
    print(manager.db_object_to_model(result[0]))
    
# (:ClassDefinitionWrapper {...})
# ...
# (:Student:Person {school:"Columbia U",name:"John",age:23})
# (:Teacher:Person {subject:"Computer Science",name:"Kate",age:30})
    

#acquire Teach class.
Teach = manager.get('Teach')

#query every edges belonging to Teach class
edges = graph.query(f"Match ()-[a:{Teach.__name__}]->() return a")
for edge in edges:
    print(edge)
# ()-[:Teach]->()

# clear the example graph
graph.delete()


```



