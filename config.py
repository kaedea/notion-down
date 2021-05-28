import json
import os
import subprocess
import typing

SYS_ENV_MAP = dict(
    token_v2="NOTION_TOKEN_V2",
)

KV = dict()


class Config:

    @staticmethod
    def load_env():
        for key, value in SYS_ENV_MAP.items():
            if os.environ.get(value) is not None:
                Config.set(key, os.environ.get(value))

    @staticmethod
    def get(key, default=None):
        if key in KV:
            return KV[key]
        return default

    @staticmethod
    def set(key, value):
        KV[key] = value

    @staticmethod
    def notion_down_version():
        return "0.0.1"

    @staticmethod
    def notion_down_revision():
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()

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
    def to_string():
        return json.dumps(KV, indent=2)
