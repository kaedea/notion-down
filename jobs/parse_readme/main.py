import os
from pathlib import Path
from shutil import copyfile

from config import Config, ArgsParser
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils, FileUtils


def start():
    print('\nHello, readme page!\n')
    channel = 'default'
    NotionWriter.clean_output()

    main_page = NotionReader.read_main_page()
    source_pages = Utils.find(main_page.children, lambda it: it.type == 'page' and str(it.title) in [
        "NotionDown README",
        "NotionDown GetTokenV2",
        "NotionDown Custom Config",
    ])

    for source_page in source_pages:
        md_page = NotionReader._parse_page(source_page)
        notion_output = NotionWriter.handle_page(md_page)[channel]

        if not notion_output.has_markdown():
            raise Exception("job fail, output md file not found: {}".format(notion_output))

        dist_dir = FileUtils.new_file(Utils.get_workspace(), "dist/parse_readme")
        FileUtils.create_dir(dist_dir)

        print("publish file to: {}".format(dist_dir))
        copyfile(notion_output.markdown_path, FileUtils.new_file(dist_dir, Path(notion_output.markdown_path).name))
        if notion_output.has_properties():
            copyfile(notion_output.properties_path, FileUtils.new_file(dist_dir, Path(notion_output.properties_path).name))
        print("done\n")


if __name__ == '__main__':
    Config.parse_configs()
    Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")

    print("")
    print("Run with configs:")
    print("config = {}".format(Config.to_string()))
    start()
