import json
import os
import subprocess

from utils.utils import Utils


DEFAULT_ARGS = {
    'config_file': None,
    'debuggable': True,
    'workspace': Utils.get_workspace(),
    'output': os.path.join(Utils.get_temp_dir(), "notion-down/outputs"),
    'token_v2': None,
    'channels': ['default'],
    'blog_url': None,
    'page_titles': ['all'],
}
SYS_ENV_MAP = {
    'token_v2': "NOTION_TOKEN_V2",
}
REQUIRED_ARGS = ['blog_url']
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
            json_obj = json.load(file_path)
            if type(json_obj) is not dict:
                raise Exception("config file should be dict:\n{}".format(json_obj))
            for k, v in json_obj:
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
                raise Exception('{} is null or not presented'.format(item))

    @staticmethod
    def to_string():
        return json.dumps(PROPERTIES, indent=2)

    @staticmethod
    def notion_down_version():
        return "0.0.1"

    @staticmethod
    def notion_down_revision():
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()


class ArgsParser:

    @staticmethod
    def parse():
        import argparse

        parser = argparse.ArgumentParser(description='Process running args.')
        for key in DEFAULT_ARGS.keys():
            # getter & setter
            Config.define_getter(key)
            Config.define_getter(key, "get_")
            Config.define_setter(key)
            if DEFAULT_ARGS[key]:
                Config.set(key, DEFAULT_ARGS[key])

            # args configs
            parser.add_argument("--{}".format(key), nargs='?', default=None)

        # parser.add_argument('--config_file', nargs='?', default=None)
        # parser.add_argument('--debug', nargs='?', default=True)
        # parser.add_argument('--workspace', nargs='?', default=Utils.get_workspace())
        # parser.add_argument('--output', nargs='?', default=os.path.join(Utils.get_temp_dir(), "notion-down/outputs"))
        # parser.add_argument('--notion_token_v2', nargs='?', default=None)
        # parser.add_argument('--channels', nargs='?', default='default')
        # parser.add_argument('--blog_url', nargs='?', default=None)
        # parser.add_argument('--page_titles', nargs='?', default='all')

        # load configs from Env parameters (lowest priority)
        Config.load_sys_env()

        # load configs from output config_file
        args = parser.parse_args()
        if args.config_file:
            Config.load_config_file(args.config_file)

        # load configs from cli input (highest priority)
        for key in DEFAULT_ARGS.keys():
            input_value = getattr(args, key)
            if input_value:
                if type(DEFAULT_ARGS[key]) is bool:
                    Config.set(key, True if str(input_value).lower() == 'True' else False)
                elif type(DEFAULT_ARGS[key]) is int:
                    Config.set(key, int(input_value))
                elif type(DEFAULT_ARGS[key]) is list:
                    # list arg divided by '|'
                    Config.set(key, [it.strip() for it in str(input_value).split("|")])
                else:
                    Config.set(key, input_value)

        # if Config.debuggable():
        #     Config.set_output(os.path.join(Config.workspace(), "build/outputs"))
        #     Config.set_token_v2(os.environ['NOTION_TOKEN_V2'])
        #     Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        #     pass

        # Config.set_debuggable(args.debug)
        # Config.set_workspace(args.workspace)
        # Config.set_output(args.output)
        # Config.set_token_v2(args.notion_token_v2)
        # Config.set_channels([it.strip() for it in str(args.channels).split("|")])
        # Config.set_blog_url(args.blog_url)
        # Config.set_page_titles([it.strip() for it in str(args.page_titles).split("|")])
