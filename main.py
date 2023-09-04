#!usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/9/1 17:14
# @Author: Wang Zhiwen

from Neo4jManager import Neo4jManager

url = "bolt://localhost:7687"
username = "neo4j"
password = "wzwtest1"

from py2neo import *

G = Graph(host="localhost", auth=(username, password))



