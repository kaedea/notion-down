import os
import urllib
from pathlib import Path

from config import Config
from notion_page import NotionPage


class NotionWriter:

    # noinspection SpellCheckingInspection
    @staticmethod
    def handle_page(notion_page: NotionPage):
        if not notion_page.is_markdown_able():
            print("Skip non-markdownable page: " + notion_page.get_identify())
            return
        if not notion_page.is_output_able():
            print("Skip non-outputable page: " + notion_page.get_identify())
            return

        print("Write page: " + notion_page.get_identify())
        page_writer = NotionPageWriter()
        target_path = os.path.join(
            notion_page.get_file_dir() if notion_page.get_file_dir() else "",
            urllib.parse.quote_plus(notion_page.get_file_name())
        )
        print("target = " + target_path)

        base_dir = os.path.join(
            Config.output(),
            page_writer.root_dir + "/" + (page_writer.post_dir if notion_page.is_published() else page_writer.draft_dir)
        )
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(base_dir, target_path + ".md")

        if os.path.exists(file_path):
            if not Config.debuggable():
                raise Exception("file already exists: " + file_path)
            pass
        else:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w+") as f:
            f.write(notion_page.get_title())


class NotionPageWriter:
    def __init__(self):
        self.root_dir = "NotionDown"
        self.assets_dir = "assets"
        self.post_dir = "post"
        self.draft_dir = "draft"


