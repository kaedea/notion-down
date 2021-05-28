import os
import shutil

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter, NotionPageWriter
from utils.utils import Utils, FileUtils


def start():
    print('\nHello, NotionDown sample posts\n')
    NotionWriter.clean_output()
    channel = 'default'

    notion_pages = NotionReader.handle_post()
    dir_outputs = NotionWriter.handle_pages(notion_pages)

    if not dir_outputs[channel] or not dir_outputs[channel].has_output():
        raise Exception("job fail, output dir not found: {}".format(dir_outputs[channel]))

    output_dir = dir_outputs[channel].output_dir
    print("get writer output dir: {}".format(output_dir))

    dist_dir = FileUtils.new_file(Utils.get_workspace(), "dist/parse_sample_posts")
    FileUtils.create_dir(dist_dir)
    print("publish file to: {}".format(dist_dir))

    # Copy dir append
    # noinspection PyArgumentList
    shutil.copytree(
        output_dir,
        dist_dir,
        dirs_exist_ok=True
    )
    print("done\n")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process some args.')
    parser.add_argument('debug', nargs='?', default=True)
    parser.add_argument('workspace', nargs='?', default=Utils.get_workspace())
    parser.add_argument('output', nargs='?', default=os.path.join(Utils.get_temp_dir(), "notion-down/outputs"))
    parser.add_argument('notion_token_v2', nargs='?', default=None)
    parser.add_argument('blog_url', nargs='?', default=None)
    parser.add_argument('channels', nargs='?', default='default')

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
    Config.set_channels(str(args.channels).split("|"))

    print("")
    print("Run with configs:")
    print("config = {}".format(Config.to_string()))

    start()
