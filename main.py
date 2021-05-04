import os

from config import Config
from utils.utils import Utils


def start():
    print('\nHello\n')


def get_workspace():
    return os.path.dirname(os.path.realpath(__file__))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process some args.')
    parser.add_argument('debug', nargs='?', default=True)
    parser.add_argument('workspace', nargs='?', default=get_workspace())
    parser.add_argument('output', nargs='?', default=os.path.join(Utils.get_temp_dir(), "notion-down/outputs"))
    parser.add_argument('notion_token_v2', nargs='?', default=None)
    parser.add_argument('blog_url', nargs='?', default=None)

    args = parser.parse_args()
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
    Config.set_blog_url(args.blog_url)

    print("")
    print("Run with configs:")
    print("config = {}".format(Config.to_string()))

    start()
