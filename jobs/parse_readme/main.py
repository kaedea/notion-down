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
    # Official API: read_main_page returns dict, not block with children.
    # We use read_all_pages to get all subpages recursively (or just use _read_post_pages logic)
    # But read_all_pages filters by config.
    # Here we want specific pages.
    # Let's use read_all_pages but we need to ensure config doesn't filter them out?
    # Config is set in __main__.
    # But here we want specific titles.
    # Let's use NotionReader._read_post_pages() which reads all from main page, then we filter.
    # Wait, _read_post_pages() applies config filter!
    # If we want ALL pages to filter manually, we might need to temporarily set config or use internal method.
    # Actually, _read_post_pages calls _recurse_read_page.
    # Let's just use _recurse_read_page manually or set Config.page_titles to ['all'] temporarily?
    # But Config is global.
    # Let's just use NotionReader.read_all_pages() and assume Config is set to 'all' (default) or we set it.
    # In __main__, Config.parse_configs() is called. Default is 'all'.
    # So read_all_pages() should return all pages.
    
    all_pages = NotionReader.read_all_pages()
    source_pages = Utils.find(all_pages, lambda it: NotionReader._get_page_title(it) in [
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
