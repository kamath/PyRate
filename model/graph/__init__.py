import json, os

from neomodel import StructuredRel, StructuredNode, IntegerProperty, FloatProperty
from abc import ABC, abstractmethod
from typing import *

class Credited(StructuredRel):
    ordinal = IntegerProperty()
    credit = FloatProperty()

class Node(StructuredNode):
    __abstract_node__ = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def exists(cls, identifier):
        raise NotImplementedError

    @classmethod
    def clean(cls, **kwargs) -> Tuple[StructuredNode, Dict[str, dict]]:
        '''
        Cleans default kwargs and instantiates the object

        :param kwargs: the params to instantiate the given StructuredNode object
        :return: the instantiated object
        '''
        raise NotImplementedError

    @classmethod
    def inst(cls, **kwargs):
        '''
        Abstract method to instantiate the object directly from the class instead of from the Node class

        :param kwargs: the args to instantiate the object
        :return: the object
        '''
        raise NotImplementedError

    @staticmethod
    def post_clean(obj, to_connect: dict) -> StructuredNode:
        '''
        Basically instantiates the object connections after instantiating the object itself

        :param obj: the object created by inst()
        :param to_connect: the nodes to connect as raw JSONs
        :return: the instantiated object with appropriate connections
        '''
        return obj

    @classmethod
    def build(cls, subclass, identifier: dict, **kwargs) -> StructuredNode:
        '''
        Instantiates the object

        :param subclass: the subclass to instantiate
        :param identifier: the dictionary containing the identifier, aka {'spotify_id': 6969420}
        :param kwargs: the remaining args to instantiate the object
        :return: the object
        '''
        e: cls = subclass.exists(identifier)

        if e:
            return e

        obj, to_connect = subclass.clean(**kwargs)
        obj.save()
        return subclass.post_clean(obj, to_connect)

def connection_url(aws=False):
    if aws:
        config_path = os.path.join('config', 'neo4j.json')
    else:
        config_path = os.path.join('sample_config', 'neo4j.json')
    neo4j_vars = json.load(open(config_path, 'r'))
    user = neo4j_vars['user']
    pw = neo4j_vars['pass']
    dns = neo4j_vars['dns']
    port = neo4j_vars['bolt_port']
    return f"bolt://{user}:{pw}@{dns}:{port}"