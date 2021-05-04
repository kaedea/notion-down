# -*- coding: utf-8 -*-

import json
import os
import tempfile
from pathlib import Path


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def pwd():
        return os.getcwd()

    @staticmethod
    def get_workspace():
        return Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute()

    @staticmethod
    def get_temp_dir():
        return tempfile.gettempdir()

    @staticmethod
    def find(array, predicate):
        finds = [it for it in array if predicate(it)]
        return finds

    @staticmethod
    def find_one(array, predicate):
        finds = [it for it in array if predicate(it)]
        if finds:
            return finds[0]
        return finds

    @staticmethod
    def parse_json(file_path):
        with open(file_path) as f:
            data = json.load(f)
        return data

    @staticmethod
    def safe_getattr(obj, name, default_value=None):
        if name in obj:
            return obj[name]
        if hasattr(obj, name):
            return getattr(obj, name)
        return default_value

    @staticmethod
    def get_props(obj):
        return [it for it in dir(obj) if not it.startswith('_')]

    @staticmethod
    def parse_bean(bean, my_dict):
        for prop in Utils.get_props(bean):
            value = Utils.safe_getattr(my_dict, prop)
            if value:
                setattr(bean, prop, value)
        return bean

    @staticmethod
    def paging(array, page, limit):
        page = int(page)
        limit = int(limit)

        if page >= 1 and limit >= 1:
            count_str = limit * (page - 1)  # 0, 20
            count_end = limit * page  # 20, 40
            count_max = len(array)
            if count_end >= count_max:
                count_end = count_max

            print(count_str)
            print(count_end)
            print(count_max)
            array = array[count_str:count_end]

        return array

    @staticmethod
    def assert_property_presented(item, properties):
        props = []
        if isinstance(properties, list):
            props = properties
        else:
            props.append(properties)

        for key in props:
            if key not in item:
                raise Exception('\'{}\' is not given: {}'.format(key, item))

    @staticmethod
    def check_property_presented(item, properties):
        props = []
        if isinstance(properties, list):
            props = properties
        else:
            props.append(properties)

        result = True
        for key in props:
            if key not in item:
                print('\'{}\' is not given: {}'.format(key, item))
                result = False
        return result
