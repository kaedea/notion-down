import os
import unittest

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils


class NotionCiTest(unittest.TestCase):

    def test_generate_markdown_showcase(self):
        Config.load_env()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))

        NotionWriter.clean_output()

        main_page = NotionReader.read_main_page()
        self.assertIsNotNone(main_page)

        test_page = Utils.find_one(main_page.children, lambda it: it and str(it.title) == "MarkDown Test Page")
        self.assertIsNotNone(test_page)

        md_page = NotionReader.handle_single_page(test_page)
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_generate_read_me(self):
        Config.load_env()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.set_page_titles(["NotionDown README"])

        NotionWriter.clean_output()

        main_page = NotionReader.read_main_page()
        self.assertIsNotNone(main_page)

        test_page = Utils.find_one(main_page.children, lambda it: it.type == 'page' and str(it.title) in Config.page_titles())
        self.assertIsNotNone(test_page)

        md_page = NotionReader.handle_single_page(test_page)
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

