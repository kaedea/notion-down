import os
import unittest

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils


class NotionHandlerTest(unittest.TestCase):

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

    def test_clean_output(self):
        NotionWriter.clean_output()

    def test_handle_write_post(self):
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

    def test_handle_write_markdown_test_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_markdown_spa_showcase_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("MarkDown Test Page - SPA")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_markdown_notion_down_solution_showcase_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("Hexo page -  NotionDown")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_markdown_readme_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown README")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_notion_obfuscating_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown Obfuscated Blocks")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_notion_nested_list_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown Nested List")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_notion_short_code_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown ShortCode")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_notion_pull_quote_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown Pullquote Blocks")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_notion_cn_en_mixing_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown CN-EN Concat Format")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_notion_down_properties_page(self):
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown Properties")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

