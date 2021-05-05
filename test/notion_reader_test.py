import os
import unittest

from config import Config
from notion_reader import NotionReader
from utils.utils import Utils


class NotionHandlerTest(unittest.TestCase):

    def test_check_token(self):
        self.assertTrue("NOTION_TOKEN_V2" in os.environ, "Token exist")

    def test_handle_post(self):
        Config.load_env()
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        notion_pages = NotionReader.handle_post()
        self.assertIsNotNone(notion_pages)
        for notion_page in notion_pages:
            notion_page.is_published()
            notion_page.get_title()
            notion_page.get_date()
            notion_page.get_category()
            notion_page.get_tag()
            notion_page.get_file_dir()
            notion_page.get_file_name()
            pass

