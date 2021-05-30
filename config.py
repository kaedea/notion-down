import json
import os
import subprocess
import typing

from utils.utils import Utils

SYS_ENV_MAP = dict(
    token_v2="NOTION_TOKEN_V2",
)

KV = dict()


class Config:

    @staticmethod
    def get(key, default=None):
        if key in KV:
            return KV[key]
        return default

    @staticmethod
    def set(key, value):
        KV[key] = value

    @staticmethod
    def load_env():
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
                KV[k] = v
        else:
            raise Exception("config file not found: {}".format(file_path))

    @staticmethod
    def debuggable():
        return Config.get("debuggable", False)

    @staticmethod
    def set_debuggable(value):
        Config.set("debuggable", value)

    @staticmethod
    def workspace():
        return Config.get("workspace", None)

    @staticmethod
    def set_workspace(value):
        Config.set("workspace", value)

    @staticmethod
    def notion_down_version():
        return "0.0.1"

    @staticmethod
    def notion_down_revision():
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()

    @staticmethod
    def output():
        return Config.get("output", None)

    @staticmethod
    def set_output(value):
        Config.set("output", value)

    @staticmethod
    def token_v2():
        return Config.get("token_v2", None)

    @staticmethod
    def set_token_v2(value):
        Config.set("token_v2", value)

    @staticmethod
    def blog_url():
        return Config.get("blog_url", None)

    @staticmethod
    def set_blog_url(value):
        Config.set("blog_url", value)

    @staticmethod
    def channels():
        return Config.get("channels", [])

    @staticmethod
    def set_channels(value: typing.List):
        Config.set("channels", value)

    @staticmethod
    def page_titles():
        return Config.get("page_titles", [])

    @staticmethod
    def set_page_titles(value: typing.List):
        Config.set("page_titles", value)

    @staticmethod
    def to_string():
        return json.dumps(KV, indent=2)


class ArgsParser:

    @staticmethod
    def parse():
        import argparse
        parser = argparse.ArgumentParser(description='Process some args.')
        parser.add_argument('config_file', nargs='?', default=None)
        parser.add_argument('debug', nargs='?', default=True)
        parser.add_argument('workspace', nargs='?', default=Utils.get_workspace())
        parser.add_argument('output', nargs='?', default=os.path.join(Utils.get_temp_dir(), "notion-down/outputs"))
        parser.add_argument('notion_token_v2', nargs='?', default=None)
        parser.add_argument('channels', nargs='?', default='default')
        parser.add_argument('blog_url', nargs='?', default=None)
        parser.add_argument('page_titles', nargs='?', default='all')

        args = parser.parse_args()
        if args.config_file:
            Config.load_config_file(args.config_file)

        if args.debug:
            args.output = os.path.join(args.workspace, "build/outputs")
            args.notion_token_v2 = os.environ['NOTION_TOKEN_V2']
            args.blog_url = "https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34"
            pass

        required_args = ['blog_url']
        for item in required_args:
            if item not in args or getattr(args, item) is None:
                raise Exception('{} is null or not presented'.format(item))

        Config.load_env()
        Config.set_debuggable(args.debug)
        Config.set_workspace(args.workspace)
        Config.set_output(args.output)
        Config.set_token_v2(args.notion_token_v2)
        Config.set_channels([it.strip() for it in str(args.channels).split("|")])
        Config.set_blog_url(args.blog_url)
        Config.set_page_titles([it.strip() for it in str(args.page_titles).split("|")])
        pass
