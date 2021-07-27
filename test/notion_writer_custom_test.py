import os
import unittest

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils


class NotionWriterCustomConfigTest(unittest.TestCase):

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

    def test_write_posts_with_channel(self):
        Config.set_channels(['GitHub'])
        NotionWriter.clean_output()

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

            NotionWriter.handle_page(notion_page)
            pass

    def test_write_markdown_test_page_with_channel(self):
        Config.set_channels(['GitHub'])
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_write_markdown_test_page_with_channels(self):
        Config.set_channels(['default', 'GitHub'])
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_write_markdown_test_page_with_channel_1(self):
        Config.set_channels(['Notion'])
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown ShortCode")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_write_markdown_test_page_with_channel_2(self):
        Config.set_channels(['Blog'])
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown ShortCode")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass


