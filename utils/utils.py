# -*- coding: utf-8 -*-

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pkg_resources


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def pwd():
        return os.getcwd()

    @staticmethod
    def get_workspace():
        return str(Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute())

    @staticmethod
    def get_temp_dir():
        return tempfile.gettempdir()

    @staticmethod
    def is_git_directory(path='.'):
        return subprocess.call(
            ['git', '-C', path, 'status'],
            stderr=subprocess.STDOUT,
            stdout=open(os.devnull, 'w')
        ) == 0

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

    @staticmethod
    def check_module_installed(name):
        try:
            pkg_resources.get_distribution(name)
            return True
        except pkg_resources.DistributionNotFound:
            return False

    @staticmethod
    def is_unittest():
        return 'unittest' in sys.modules.keys()

    @staticmethod
    def escape_yaml_string(value):
        """
        Escape YAML string values to prevent parsing errors.
        Wraps strings in quotes if they contain special characters.
        
        Args:
            value: The value to escape (will be converted to string)
            
        Returns:
            str: Properly escaped YAML string value
            
        Examples:
            >>> Utils.escape_yaml_string("simple")
            'simple'
            >>> Utils.escape_yaml_string("title: with colon")
            '"title: with colon"'
            >>> Utils.escape_yaml_string('has "quotes"')
            '"has \\"quotes\\""'
        """
        if not value:
            return '""'
        
        value_str = str(value)
        
        # Characters that require quoting in YAML
        special_chars = [':', '#', '@', '`', '"', "'", '!', '%', '&', '*', '{', '}', '[', ']', '|', '>', '<', '?', '-', ',']
        
        # Check if value needs quoting
        needs_quoting = False
        
        # Check for special characters
        for char in special_chars:
            if char in value_str:
                needs_quoting = True
                break
        
        # Check if starts/ends with whitespace
        if value_str != value_str.strip():
            needs_quoting = True
        
        # Check if it looks like a number or boolean
        if value_str.lower() in ['true', 'false', 'yes', 'no', 'on', 'off', 'null', '~']:
            needs_quoting = True
        
        if not needs_quoting:
            return value_str
        
        # Escape double quotes and backslashes
        escaped = value_str.replace('\\', '\\\\').replace('"', '\\"')
        
        # Wrap in double quotes
        return '"{}"'.format(escaped)

    @staticmethod
    def format_yaml_value(value):
        """
        Format a value for YAML output, preserving proper types.
        
        Args:
            value: The value to format (can be any type)
            
        Returns:
            str: Properly formatted YAML value
            
        Examples:
            >>> Utils.format_yaml_value(True)
            'true'
            >>> Utils.format_yaml_value(False)
            'false'
            >>> Utils.format_yaml_value(42)
            '42'
            >>> Utils.format_yaml_value("simple")
            'simple'
            >>> Utils.format_yaml_value("title: with colon")
            '"title: with colon"'
        """
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Only escape strings, preserving their string nature
            return Utils.escape_yaml_string(value)
        else:
            # For other types, convert to string and escape
            return Utils.escape_yaml_string(str(value))

    @staticmethod
    def parse_value_type(value):
        """
        Parse a string value and try to convert it to appropriate type (bool, int, float, or keep as string).
        
        Args:
            value: The value to parse (usually a string from Notion properties)
            
        Returns:
            The value converted to appropriate type
            
        Examples:
            >>> Utils.parse_value_type("true")
            True
            >>> Utils.parse_value_type("false")
            False
            >>> Utils.parse_value_type("42")
            42
            >>> Utils.parse_value_type("3.14")
            3.14
            >>> Utils.parse_value_type("hello")
            'hello'
        """
        if not isinstance(value, str):
            return value
        
        # Try to parse as boolean
        if value.lower() in ['true', 'yes', 'on']:
            return True
        elif value.lower() in ['false', 'no', 'off']:
            return False
        
        # Try to parse as integer
        try:
            if '.' not in value and 'e' not in value.lower():
                return int(value)
        except ValueError:
            pass
        
        # Try to parse as float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string if no conversion is possible
        return value


class FileUtils:
    @staticmethod
    def new_file(file_dir, file_name):
        return os.path.join(file_dir, file_name)

    @staticmethod
    def exists(file_path):
        return Path(file_path).exists()

    @staticmethod
    def create_file(file_path, fore=False):
        path = Path(file_path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)

        if path.is_dir():
            if not fore:
                raise Exception("{} is dir".format(file_path))
            shutil.rmtree(path.absolute())
            path.touch(exist_ok=True)

    @staticmethod
    def create_dir(file_path, fore=False):
        path = Path(file_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            return
        if path.is_file():
            if not fore:
                raise Exception("{} is file".format(file_path))
            os.remove(path.absolute())
            path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def clean_dir(file_path, fore=False):
        FileUtils.delete_dir(file_path, fore)
        FileUtils.create_dir(file_path, fore)

    @staticmethod
    def delete_dir(file_path, fore=False):
        path = Path(file_path)
        if path.is_file():
            if not fore:
                raise Exception("{} is file".format(file_path))
            os.remove(path.absolute())
            return
        if path.exists():
            shutil.rmtree(file_path)

    @staticmethod
    def delete(file_path):
        path = Path(file_path)
        if path.is_file():
            os.remove(path.absolute())
            return
        if path.exists():
            shutil.rmtree(file_path)

    @staticmethod
    def write_text(text, file_path, mode="w+"):
        with open(file_path, mode) as f:
            f.write(text)

