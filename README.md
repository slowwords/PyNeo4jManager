# Neo4jManager

#### 声明对象

```
url = ''
username = ''
password = ''
ob = Neo4jManager(url, username, password)
```

#### 节点命名

对于单标签节点，可以调用_name_node()方法命名一个节点

```
node = ob._name_node(
	node_name="p",
    node_label="Employee",	
    node_property={
        "name":"test",
        "location": "China"
    }
)
```

对于多标签节点，将node_label以元组或者列表的形式传入

```
node = ob._name_node(
	node_name="p",
    node_label=("Employee","label2"),
    node_property={
        "name":"test",
        "location": "China"
    }
)
```

节点属性node_property可以为None

```python
node = ob._name_node(
	node_name="p",
    node_label=("Employee","label2")
)
```

#### 关系命名

通过调用__name_connection()方法命名关系。

```
connection = ob._name_connection(
	connection_name="r",
        connection_label="DO_SHOPPING_WITH",
        connection_property={
            "shopdate": "12/12/2014",
            "price": 55000
        }
)
```

其中connection_property也是可选的。

```
connection = 0b._name_connection(
	connection_name="r",
    connection_label="DO_SHOPPING_WITH",
)
```

#### CREATE

实现的Neo4jManager中，将上述所有的创建方法封装到了同一个方法create_node()中。

```
- 创建无属性的节点
CREATE (emp:Employee)
res = ob.create(
    ob._name_node(node_name="emp", node_label="Employee")
)	# 返回值为True or False
# emp 是一个节点名。Employee 是 emp 节点的标签名称。

- 创建有属性的节点
CREATE (dept:Dept { deptno:10,dname:"Accounting",location:"Hyderabad" })
ob.create(
	ob._name_node(
    	node_name="dept",
        node_label="Dept",
        node_property={"deptno":10,
                       "dname":"Accounting",
                       "location":"Hyderabad"}
    )
)
# dept是一个节点名。Dept是emp节点的标签名称。大括号里是Dept的数据

- 创建多个标签到节点
CREATE (m:Movie:Cinema:Film:Picture)
ob.create(
	ob._name_node(node_name="m",node_label=("Movie","Cinema","Film","Picture"))
)
# 这里m是一个节点名，Movie, Cinema, Film, Picture是m节点的多个标签名称

- 创建带有关系（无属性）的多节点（无属性）
CREATE (fb1:FaceBookProfile1)-[like:LIKES]->(fb2:FaceBookProfile2) 
ob.create(
    ob._name_node(node_name="fb1", node_label="FaceBookProfile1"),
    ob._name_connection(connection_name="like", connection_label="LIKES"),
    ob._name_node("fb2", "FaceBookProfile2")
)
# 关系名称是“LIKES” 关系标签是“like”

- 创建带有关系（有属性）的多节点（有属性）
CREATE (video1:YoutubeVideo1{title:"Action Movie1",updated_by:"Abc",uploaded_date:"10/10/2010"})-[movie:ACTION_MOVIES{rating:1}]->(video2:YoutubeVideo2{title:"Action Movie2",updated_by:"Xyz",uploaded_date:"12/12/2012"}) 
ob.create(
        ob._name_node(
            "video1",
            "YoutubeVideo1",
            {"title": "Action Movie1", "updated_by": "Abc", "uploaded_date": "10/10/2010"}
        ),
        ob._name_connection(
            "movie",
            "ACTION_MOVIES",
            {"rating": 1}
        ),
        ob._name_node(
            "video2",
            "YoutubeVideo2",
            {"title": "Action Movie2", "updated_by": "Xyz", "uploaded_date": "12/12/2012"}
        )
    )
```

#### MATCH

这一部分的实现分为了两个方法，分别是不使用where命令的节点查询、关系查询、查询并创建节点关系的方法match()和使用where的节点查询、查询并创建节点关系的方法match_where()。

```
- 查询节点内容

MATCH (dept:Dept) return dept
res = ob.match(ob._name_node("dept", "Dept"))	# 返回值为一个列表，存放所有符合条件的item
# 查询Dept下的内容

MATCH (p:Employee {id:123,name:"Lokesh"}) RETURN p
ob.match(ob._name_node(
        "p",
        "Employee",
        {"id": 123, "name": "Lokesh"}
    ))
# 查询Employee标签下 id=123，name="Lokesh"的节点

MATCH (p:Employee) WHERE p.name = "Lokesh" RETURN p.id,p.name
ob.match_where(
        node=ob._name_node("p", "Employee"),
        match_property={"name": "Lokesh"},
        return_property=("id", "name")
    )
# 查询Employee标签下name="Lokesh"的节点，使用（where命令,类比sql）

- 查询节点关系
MATCH (cust)-[r:DO_SHOPPING_WITH]->(cc) RETURN cust,cc
ob.match(
        node=ob._name_node("cust"),
        connection=ob._name_connection("r", "DO_SHOPPING_WITH"),
        node2=ob._name_node("cc")
    )
# 关系名称为“DO_SHOPPING_WITH”  关系标签为“r”。若报错，则可能未创建cust,cc

- 查询并创建节点关系
	
MATCH (e:Customer),(cc:CreditCard)  CREATE (e)-[r:DO_SHOPPING_WITH ]->(cc) 
ob.match(
        node=ob._name_node("e", "Customer"),
        node2=ob._name_node("cc", "CreditCard"),
        connection=ob._name_connection("r", "DO_SHOPPING_WITH"),
        if_create_connection=True
    )
# 关系名称为“DO_SHOPPING_WITH”  关系标签为“r”，关系为e->c,关系无属性

MATCH (cust:Customer),(cc:CreditCard) CREATE (cust)-[r:DO_SHOPPING_WITH{shopdate:"12/12/2014",price:55000}]->(cc) RETURN r
ob.match(
        node=ob._name_node("cust", "Customer"),
        node2=ob._name_node("cc", "CreditCard"),
        connection=ob._name_connection(
            "r",
            "DP_SHOPPING_WITH",
            {"shopdate": "12/12/2014", "price": 55000}
        ),
        if_create_connection=True
    )
# 关系名称为“DO_SHOPPING_WITH”  关系标签为“r”，关系为e->c,关系有属性shopdate、price。

- 查询并创建节点关系
MATCH (cust:Customer),(cc:CreditCard) WHERE cust.id = "1001" AND cc.id= "5001" CREATE (cust)-[r:DO_SHOPPING_WITH{shopdate:"12/12/2014",price:55000}]->(cc) RETURN r
ob.match_where(
        node=ob._name_node("cust", "Customer"),
        match_property={"id": "1001"},
        node2=ob._name_node("cc", "CreditCard"),
        match_property2={"id": "5001"},
        connection=ob._name_connection("r", "DO_SHOPPING_WITH", {"shopdate": "12/12/2014", "price": 55000}),
        if_create_connection=True
    )
```

#### DELETE

这一部分全部封装到方法delete()中。

```
- 删除节点 
MATCH (e: Employee) DELETE e
res = ob.delete(
        ob._name_node("e", "Employee")
    )	# 返回True or False
- DELETE节点和关系
MATCH (cc: CreditCard)-[rel]-(c:Customer) DELETE cc,c,rel
ob.delete(
        ob._name_node("cc", "CreditCard"),
        ob._name_node("c", "Customer"),
        ob._name_connection("r")
    )
- 删除所有关系及节点
MATCH (n)OPTIONAL MATCH (n)-[r]-()DELETE n,r
ob.delete(
        node=ob._name_node("n"),
        connection=ob._name_connection("r"),
        if_all=True
    )
```

#### REMOVE

用于删除节点的某一属性或者标签

```
- 删除节点/关系
MATCH (book { id:122 }) REMOVE book.price RETURN book
ob.remove(
        ob._name_node("book", node_property={"id": 122}),
        remove_property=("price")
    )
# “价格”属性被删除
- 删除标签
MATCH (m:Movie) REMOVE m:Picture
ob.remove(
        ob._name_node("m", "Movie"),
        remove_label="Picture",
    )
```

#### SET

```
- 更新节点属性值
MATCH (book:Book) SET book.title = 'superstar' RETURN book
ob.set(
        ob._name_node("book", "Book"),
        property={"title": "superstar"}
    )
```

