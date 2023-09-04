#!usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/9/1 17:15
# @Author: Wang Zhiwen

from neo4j import GraphDatabase
from py2neo import Graph

class Neo4jManager:

    def __init__(self, url='localhost', username='', password=''):
        # self.driver = GraphDatabase.driver(url, auth=(username, password))
        self.graph = Graph(host=url, auth=(username, password))

    def close_connection(self):
        del self.graph  # py2neo没有提供关闭连接的方法

    def open_connection(self):
        self.graph = Graph(host=url, auth=(username, password))

    def __execute_query(self, query):
        result = self.graph.run(query)
        # with self.driver.session() as session:
        #     result = session.run(query)
        return result

    @staticmethod
    def _name_node(node_name=None, node_label=None, node_property=None):
        return {
            "node_name": node_name,
            "node_label": node_label,
            "node_property": node_property
        }

    def __check_if_Neo4jManager_node(self, node):
        assert isinstance(node, dict)
        assert 'node_name' in node.keys()
        assert 'node_label' in node.keys()
        assert 'node_property' in node.keys()
        if node['node_property']:
            assert isinstance(node['node_property'], dict)

    @staticmethod
    def _name_connection(connection_name, connection_label=None, connection_property=None):
        if connection_property:
            assert isinstance(connection_property, dict)
        return {
            "c_name": connection_name,
            "c_label": connection_label,
            "c_property": connection_property
        }

    def __check_if_Neo4jManager_connection(self, connection):
        assert isinstance(connection, dict)
        assert 'c_name' in connection.keys()
        assert 'c_label' in connection.keys()
        assert 'c_property' in connection.keys()

    def __node_query(self, node, property=True):
        if not node['node_name']:
            return ""
        query = f"({node['node_name']}"
        # label
        if node['node_label']:
            query += ":"
            if not (isinstance(node['node_label'], tuple) or isinstance(node['node_label'], list)):
                node['node_label'] = [node['node_label']]
            assert isinstance(node['node_label'][0], str)
            for l in node['node_label']:
                query += f"{l}:"
            query = query[:-1]

        # property
        if node['node_property'] and property:
            assert isinstance(node['node_property'], dict)  # property必须以字典形式传入，否则非法
            query += "{"
            for k, v in node['node_property'].items():
                query += f"{k}:"
                if isinstance(v, str):
                    query += f'"{v}",'
                else:
                    query += f"{v},"
            query = query[:-1] + "}"

        query += ")"
        return query

    def __connection_query(self, connection):
        if connection:
            self.__check_if_Neo4jManager_connection(connection)
            if connection['c_label']:
                query = f"-[{connection['c_name']}:{connection['c_label']}"
            else:
                query = f"-[{connection['c_name']}"
            if connection['c_property']:
                query += '{'
                for k, v in connection['c_property'].items():
                    if isinstance(v, str):
                        query += f'{k}:"{v}",'
                    else:
                        query += f"{k}:{v},"
                query = query[:-1] + "}"
            query += "]->"
        else:
            query = ""
        return query

    def create(self, node1, connection=None, node2=None):
        """
        :param node1: Neo4jManager.node
        :param connection: Neo4jManager.connection
        :param node2: Neo4jManager.node
        :return: True or False
        """
        self.__check_if_Neo4jManager_node(node1)
        query = f"CREATE " + self.__node_query(node1)
        if connection:
            self.__check_if_Neo4jManager_connection(connection)
            query += self.__connection_query(connection)
        if node2:
            self.__check_if_Neo4jManager_node(node2)
            query += self.__node_query(node2)
        result = self.__execute_query(query)
        if result:
            return True
        else:
            return False

    def __match_node(self, node1, connection=None, node2=None):
        assert node1 is not None
        query = f"MATCH " + self.__node_query(node1)
        if connection:
            query += self.__connection_query(connection)
        if node2:
            query += self.__node_query(node2)
        if node2:
            query = query + f" RETURN {node1['node_name']}, {node2['node_name']}"
        else:
            query += f" RETURN {node1['node_name']}"
        return self.__execute_query(query).data()

    def __match_node_where(self, node, match_property, return_property):
        assert node, match_property is not None
        query = "MATCH" + self.__node_query(node, property=False) + " WHERE "
        for k, v in match_property.items():
            if isinstance(v, str):
                name = node['node_name']
                query += f'{name}.{k}="{v}" AND '
            else:
                query += f"{node['node_name']}.{k}={v} AND "
        query = query[:-4]
        query += "RETURN "
        for r in return_property:
            query += f"{node['node_name']}.{r},"
        query = query[:-1]
        return self.__execute_query(query).data()

    def __match_create_connection(self, node1, node2, connection):
        query = "MATCH " + self.__node_query(node1, property=False) +\
                "," + self.__node_query(node2, property=False) + " " +\
                "CREATE " + f"({node1['node_name']})" +\
                self.__connection_query(connection) +\
                 f"({node2['node_name']}) RETURN {connection['c_name']}"
        return self.__execute_query(query).data()

    def __match_create_connection_where(self, node1, node2, match_property1, match_property2, connection):
        query = "MATCH " + self.__node_query(node1, property=False) + "," +\
                self.__node_query(node2, property=False) + " WHERE "
        for k, v in match_property1.items():
            if isinstance(v, str):
                name = node1['node_name']
                query += f'{name}.{k}="{v}" AND '
            else:
                query += f"{node1['node_name']}.{k}={v} AND "
        for k, v in match_property2.items():
            if isinstance(v, str):
                name = node2['node_name']
                query += f'{name}.{k}="{v}" AND '
            else:
                query += f"{node2['node_name']}.{k}={v} AND "
        query = query[:-4] + f"CREATE ({node1['node_name']})" + self.__connection_query(connection) +\
                f"({node2['node_name']})" + f" RETURN {connection['c_name']}"
        return self.__execute_query(query).data()

    def match(self, node, node2=None, connection=None, if_create_connection=False):
        """
        :param node: Neo4jManager.node
        :param node2: Neo4jManager.node
        :param connection: Neo4jManager.connection
        :param if_create_connection: True for MATCH and CREATE, False for MATCH only
        :return: data list
        """
        self.__check_if_Neo4jManager_node(node)
        if node2 and connection:
            self.__check_if_Neo4jManager_node(node2)
            self.__check_if_Neo4jManager_connection(connection)
            if if_create_connection:
                return self.__match_create_connection(node, node2, connection)
            else:
                return self.__match_node(node, connection, node2)
        else:
            return self.__match_node(node)

    def match_where(self, node, match_property, node2=None, match_property2=None,
                    connection=None, return_property=None, if_create_connection=False):
        """
        :param node: Neo4jManager.node
        :param match_property: dict
        :param node2: Neo4jManager.node
        :param match_property2: dict
        :param connection: Neo4jManager.connection
        :param return_property: list or tuple
        :param if_create_connection: True for MATCH and CREATE, False for MATCH only
        :return: data list
        """
        self.__check_if_Neo4jManager_node(node)
        assert isinstance(match_property, dict)
        if node2 is None:
            assert isinstance(return_property, list) or isinstance(return_property, tuple)
            return self.__match_node_where(node, match_property, return_property)
        if connection and if_create_connection:
            self.__check_if_Neo4jManager_node(node2)
            self.__check_if_Neo4jManager_connection(connection)
            assert isinstance(match_property2, dict)
            return self.__match_create_connection_where(node, node2, match_property, match_property2, connection)

    def __delete_node(self, node):
        assert isinstance(node, dict)
        query = f"MATCH " + self.__node_query(node) + " DELETE " + f"{node['node_name']}"
        result = self.__execute_query(query)
        if result:
            return True
        else:
            return False

    def __delete_node_connection(self, node1, node2, connection):
        assert isinstance(node1, dict)
        assert isinstance(node2, dict)
        assert isinstance(connection, dict)
        query = "MATCH " + self.__node_query(node1) +\
                self.__connection_query(connection)[:-1] +\
                self.__node_query(node2) +\
                f" DELETE {node1['node_name']}, {node2['node_name']}, {connection['c_name']}"
        result = self.__execute_query(query)
        if result:
            return True
        else:
            return False

    def __delete_all(self, node, connection):
        assert isinstance(node, dict)
        assert isinstance(connection, dict)
        query = f"MATCH ({node['node_name']}) OPTIONAL MATCH ({node['node_name']})" +\
                self.__connection_query(connection)[:-1] +\
                f"() DELETE {node['node_name']}, {connection['c_name']}"
        result = self.__execute_query(query)
        if result:
            return True
        else:
            return False

    def delete(self, node, node2=None, connection=None, if_all=False):
        """
        :param node: Neo4jManager.node
        :param node2: Neo4jManager.node
        :param connection: Neo4jManager.connection
        :param if_all: True for deleting all and False for others
        :return: True or False
        """
        self.__check_if_Neo4jManager_node(node)
        if if_all:
            self.__check_if_Neo4jManager_connection(connection)
            return self.__delete_all(node, connection)
        else:
            if node2 and connection:
                self.__check_if_Neo4jManager_node(node2)
                self.__check_if_Neo4jManager_node(connection)
                return self.__delete_node_connection(node, node2, connection)
            else:
                return self.__delete_node(node)

    def __remove_label(self, node, remove_label):
        assert isinstance(node, dict)
        if not (isinstance(remove_label, list) or isinstance(remove_label, tuple)):
            remove_label = [remove_label]
        query = "MATCH " + self.__node_query(node) + " REMOVE "
        for rl in remove_label:
            query += f"{node['node_name']}:{rl},"
        query = query[:-1]
        result = self.__execute_query(query)
        if result:
            return True
        else:
            return False

    def __remove_property(self, node, remove_property):
        assert isinstance(node, dict)
        assert remove_property is not None
        if not (isinstance(remove_property, list) or isinstance(remove_property, tuple)):
            remove_property = [remove_property]
        query = "MATCH " + self.__node_query(node) + f" REMOVE "
        for rp in remove_property:
            query += f"{node['node_name']}.{rp},"
        query = query[:-1] + f" RETURN {node['node_name']}"
        result = self.__execute_query(query)
        if result:
            return True
        else:
            return False

    def remove(self, node, remove_property=None, remove_label=None):
        """
        :param node:
        :param remove_property:
        :param remove_label:
        :return: True or False
        """
        self.__check_if_Neo4jManager_node(node)
        if remove_property:
            return self.__remove_property(node, remove_property)
        if remove_label:
            return self.__remove_label(node, remove_label)

    def set(self, node, property):
        """
        :param node: Neo4jManager.node
        :param property: dict
        :return: True or False
        """
        self.__check_if_Neo4jManager_node(node)
        assert isinstance(property, dict)
        query = "MATCH " + self.__node_query(node) + " SET "
        for k, v in property.items():
            query += f"{node['node_name']}.{k} = " + f'"{v}",'
        query = query[:-1] + f" RETURN {node['node_name']}"
        result = self.__execute_query(query)
        if result:
            return True
        else:
            return False

if __name__ == "__main__":
    # url = 'bolt://localhost:7687'
    url = "localhost"
    username = 'neo4j'
    password = 'wzwtest1'
    ob = Neo4jManager(url, username, password)
    result = ob.create(
        ob._name_node("n", "Node", {"age": 11, "name": "test"})
    )
    r = ob.match(
        ob._name_node("n", "Node")
    )
    ob.close_connection()
    # --------------------------
    # test CREATE
    # --------------------------
    # 创建无属性节点
    # ob.create(
    #     ob._name_node(node_name="emp", node_label="Employee")
    # )
    # # 创建有属性节点
    # ob.create(
    #     ob._name_node(
    #         node_name="dept",
    #         node_label="Dept",
    #         node_property={"deptno": 10,
    #                        "dname": "Accounting",
    #                        "location": "Hyderabad"}
    #     )
    # )
    # # 创建多标签节点
    # ob.create(
    #     ob._name_node(node_name="m", node_label=("Movie", "Cinema", "Film", "Picture"))
    # )
    # # 创建带有关系（无属性）的多节点（无属性）
    # ob.create_node(
    #     ob._name_node(node_name="fb1", node_label="FaceBookProfile1"),
    #     ob._name_connection(connection_name="like", connection_label="LIKES"),
    #     ob._name_node("fb2", "FaceBookProfile2")
    # )
    # # 创建带有关系（有属性）的多节点（有属性）
    # ob.create(
    #     ob._name_node(
    #         "video1",
    #         "YoutubeVideo1",
    #         {"title": "Action Movie1", "updated_by": "Abc", "uploaded_date": "10/10/2010"}
    #     ),
    #     ob._name_connection(
    #         "movie",
    #         "ACTION_MOVIES",
    #         {"rating": 1}
    #     ),
    #     ob._name_node(
    #         "video2",
    #         "YoutubeVideo2",
    #         {"title": "Action Movie2", "updated_by": "Xyz", "uploaded_date": "12/12/2012"}
    #     )
    # )
    #
    # # ------------------------------------
    # # test MATCH
    # # ------------------------------------
    # # MATCH (dept:Dept) return dept
    # print(ob.match(ob._name_node("dept", "Dept")))
    # # MATCH (p:Employee {id:123,name:"Lokesh"}) RETURN p
    # print(ob.match(ob._name_node(
    #     "p",
    #     "Employee",
    #     {"id": 123, "name": "Lokesh"}
    # )))
    # # MATCH (p:Employee) WHERE p.name = "Lokesh" RETURN p.id,p.name
    # print(ob.match_where(
    #     node=ob._name_node("p", "Employee"),
    #     match_property={"name": "Lokesh"},
    #     return_property=("id", "name")
    # ))
    # # 查询节点关系
    # # MATCH (cust)-[r:DO_SHOPPING_WITH]->(cc) RETURN cust,cc
    # print(ob.match(
    #     node=ob._name_node("cust"),
    #     connection=ob._name_connection("r", "DO_SHOPPING_WITH"),
    #     node2=ob._name_node("cc")
    # ))
    # # MATCH (e:Customer),(cc:CreditCard)  CREATE (e)-[r:DO_SHOPPING_WITH ]->(cc)
    # print(ob.match(
    #     node=ob._name_node("e", "Customer"),
    #     node2=ob._name_node("cc", "CreditCard"),
    #     connection=ob._name_connection("r", "DO_SHOPPING_WITH"),
    #     if_create_connection=True
    # ))
    # # MATCH (cust:Customer),(cc:CreditCard) CREATE (cust)-[r:DO_SHOPPING_WITH{shopdate:"12/12/2014",price:55000}]->(cc) RETURN r
    # print(ob.match(
    #     node=ob._name_node("cust", "Customer"),
    #     node2=ob._name_node("cc", "CreditCard"),
    #     connection=ob._name_connection(
    #         "r",
    #         "DP_SHOPPING_WITH",
    #         {"shopdate": "12/12/2014", "price": 55000}
    #     ),
    #     if_create_connection=True
    # ))
    # # where查询并创建节点关系
    # # MATCH (cust:Customer),(cc:CreditCard) WHERE cust.id = "1001" AND cc.id= "5001" CREATE (cust)-[r:DO_SHOPPING_WITH{shopdate:"12/12/2014",price:55000}]->(cc) RETURN r
    # print(ob.match_where(
    #     node=ob._name_node("cust", "Customer"),
    #     match_property={"id": "1001"},
    #     node2=ob._name_node("cc", "CreditCard"),
    #     match_property2={"id": "5001"},
    #     connection=ob._name_connection("r", "DO_SHOPPING_WITH", {"shopdate": "12/12/2014", "price": 55000}),
    #     if_create_connection=True
    # ))

    # ---------------------------------
    # DELETE
    # ---------------------------------
    # 删除单个节点
    # MATCH (e: Employee) DELETE e
    # print(ob.delete(
    #     ob._name_node("e", "Employee")
    # ))
    # DELETE节点和关系
    # MATCH (cc: CreditCard)-[rel]-(c:Customer) DELETE cc,c,rel
    # print(ob.delete(
    #     ob._name_node("cc", "CreditCard"),
    #     ob._name_node("c", "Customer"),
    #     ob._name_connection("r")
    # ))
    # 删除所有关系及节点
    # MATCH (n)OPTIONAL MATCH (n)-[r]-()DELETE n,r
    # print(ob.delete(
    #     node=ob._name_node("n"),
    #     connection=ob._name_connection("r"),
    #     if_all=True
    # ))

    # ------------------------
    # REMOVE
    # ------------------------
    # 删除标签
    # MATCH (m:Movie) REMOVE m:Picture
    # print(ob.remove_label(
    #     ob._name_node("m", "Movie"),
    #     remove_label="Picture",
    # ))
    # MATCH (book { id:122 }) REMOVE book.price RETURN book
    # a = ob.remove(
    #     ob._name_node("book", node_property={"id": 122}),
    #     remove_property=("price")
    # )

    # ---------------------------------
    # SET
    # ---------------------------------
    # 更新节点属性值
    # # MATCH (book:Book) SET book.title = 'superstar' RETURN book
    # b = ob.set(
    #     ob._name_node("book", "Book"),
    #     property={"title": "superstar"}
    # )