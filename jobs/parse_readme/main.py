import os
from shutil import copyfile

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils, FileUtils


def start():
    print('\nHello, readme page!\n')
    NotionWriter.clean_output()

    main_page = NotionReader.read_main_page()
    test_page = Utils.find_one(main_page.children, lambda it: it and str(it.title) == "NotionDown README")
    md_page = NotionReader.handle_single_page(test_page)
    file_path = NotionWriter.handle_page(md_page)
    if not FileUtils.exists(file_path):
        raise Exception("job fail, file not found: {}".format(file_path))
        pass

    dist_dir_path = FileUtils.new_file(Utils.get_workspace(), "dist/parse_readme/README.md")
    FileUtils.create_file(dist_dir_path)

    print("publish file to: {}".format(dist_dir_path))
    copyfile(file_path, dist_dir_path)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process some args.')
    parser.add_argument('debug', nargs='?', default=True)
    parser.add_argument('workspace', nargs='?', default=Utils.get_workspace())
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
