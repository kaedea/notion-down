import json
import os
import subprocess

from utils.utils import Utils

DEFAULT_ARGS = {
    'config_file': None,
    'debuggable': True,
    'workspace': Utils.get_workspace(),
    'output': os.path.join(Utils.get_workspace(), "build"),
    'token_v2': None,
    'writer': 'notion',
    'channels': ['default'],
    'blog_url': None,
    'page_titles': ['all'],
    'page_titles_match': [],
    'download_image': False,
}
SYS_ENV_MAP = {
    'token_v2': "NOTION_TOKEN_V2",
    'blog_url': "NOTION_TOKEN_BLOG_URL",
}
REQUIRED_ARGS = [
    'token_v2',
    'blog_url',
]
REQUIRED_MODULES = [
    'notion',
]
PROPERTIES = {}


class Config:

    @staticmethod
    def get(key, default=None):
        if key in PROPERTIES:
            return PROPERTIES[key]
        return default

    @staticmethod
    def set(key, value):
        PROPERTIES[key] = value

    @staticmethod
    def load_sys_env():
        for key, value in SYS_ENV_MAP.items():
            if os.environ.get(value) is not None:
                Config.set(key, os.environ.get(value))

    @staticmethod
    def load_config_file(file_path):
        if os.path.exists(file_path):
            json_obj = Utils.parse_json(file_path)
            if type(json_obj) is not dict:
                raise Exception("config file should be dict:\n{}".format(json_obj))
            for k in json_obj:
                v = json_obj[k]
                PROPERTIES[k] = v
        else:
            raise Exception("config file not found: {}".format(file_path))

    @staticmethod
    def define_getter(name, prefix=''):
        def get_block(value=None):
            return Config.get(name, value)
        setattr(Config, prefix + name, get_block)

    @staticmethod
    def define_setter(name):
        def set_block(value=None):
            if value:
                Config.set(name, value)
            return Config.get(name)
        setattr(Config, 'set_' + name, set_block)

    # @staticmethod
    # def debuggable():
    #     return Config.get("debuggable", False)

    # @staticmethod
    # def set_debuggable(value):
    #     Config.set("debuggable", value)

    # @staticmethod
    # def workspace():
    #     return Config.get("workspace", None)
    #
    # @staticmethod
    # def set_workspace(value):
    #     Config.set("workspace", value)

    # @staticmethod
    # def output():
    #     return Config.get("output", None)
    #
    # @staticmethod
    # def set_output(value):
    #     Config.set("output", value)

    # @staticmethod
    # def token_v2():
    #     return Config.get("token_v2", None)
    #
    # @staticmethod
    # def set_token_v2(value):
    #     Config.set("token_v2", value)

    # @staticmethod
    # def blog_url():
    #     return Config.get("blog_url", None)
    #
    # @staticmethod
    # def set_blog_url(value):
    #     Config.set("blog_url", value)
    #
    # @staticmethod
    # def channels():
    #     return Config.get("channels", [])
    #
    # @staticmethod
    # def set_channels(value: typing.List):
    #     Config.set("channels", value)
    #
    # @staticmethod
    # def page_titles():
    #     return Config.get("page_titles", [])
    #
    # @staticmethod
    # def set_page_titles(value: typing.List):
    #     Config.set("page_titles", value)

    @staticmethod
    def parse_configs():
        ArgsParser.parse()

    @staticmethod
    def check_required_args():
        for item in REQUIRED_ARGS:
            if item not in PROPERTIES or PROPERTIES[item] is None:
                raise Exception('\'{}\' is null or not presented, configure it in sys_env | config_file | cli_args !'.format(item))

    @staticmethod
    def check_required_modules():
        for module in REQUIRED_MODULES:
            if not Utils.check_module_installed(module):
                raise Exception("{} not installed, pls exec 'pip install {}' first!".format(module, module))

    @staticmethod
    def to_string():
        return json.dumps(PROPERTIES, indent=2)

    @staticmethod
    def notion_down_version():
        return "0.2.2"

    @staticmethod
    def notion_down_revision():
        if Utils.is_git_directory():
            return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        else:
            return Config.notion_down_version()


class ArgsParser:

    @staticmethod
    def parse():
        # 1. Config getter & setter
        for key in DEFAULT_ARGS.keys():
            Config.define_getter(key)
            Config.define_getter(key, "get_")
            Config.define_setter(key)

        # 2. Load default values (lowest priority)
        for key in DEFAULT_ARGS.keys():
            if DEFAULT_ARGS[key]:
                Config.set(key, DEFAULT_ARGS[key])

        # 3. load configs from SysEnv parameters
        Config.load_sys_env()

        # 4. Load configs from cli input (highest priority)
        import argparse
        parser = argparse.ArgumentParser(description='Process running args.')
        for key in DEFAULT_ARGS.keys():
            parser.add_argument("--{}".format(key), nargs='?', default=None)

        if Utils.is_unittest():
            # don NOT parse args when running from unittest
            cli_args = {key: None for key in DEFAULT_ARGS.keys()}
        else:
            cli_args = parser.parse_args()

        for key in DEFAULT_ARGS.keys():
            input_value = cli_args[key] if type(cli_args) is dict else getattr(cli_args, key)
            if input_value:
                # load configs from output config_file
                if key == 'config_file':
                    Config.load_config_file(input_value)
                # parse cli input args
                if type(DEFAULT_ARGS[key]) is bool:
                    Config.set(key, True if str(input_value).lower() == 'true' else False)
                elif type(DEFAULT_ARGS[key]) is int:
                    Config.set(key, int(input_value))
                elif type(DEFAULT_ARGS[key]) is list:
                    # list arg divided by '|'
                    Config.set(key, [it.strip() for it in str(input_value).split("|")])
                else:
                    Config.set(key, input_value)

