import os
import unittest

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils


class NotionCiTest(unittest.TestCase):

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

    def test_generate_markdown_showcase(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_generate_read_me(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown README")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass
