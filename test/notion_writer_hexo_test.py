import os
import unittest

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils


class NotionWriterHexoIntegrationTest(unittest.TestCase):

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

    def test_write_page_with_hexo_channel(self):
        Config.set_channels(['Hexo'])
        NotionWriter.clean_output()
        notion_page = NotionReader.handle_page_with_title("Hexo page - Japanese Test")
        self.assertIsNotNone(notion_page)
        NotionWriter.handle_page(notion_page)

    def test_write_page_with_hexo_channel_2(self):
        Config.set_channels(['Hexo'])
        NotionWriter.clean_output()
        notion_page = NotionReader.handle_page_with_title("Hexo page - elements showcase")
        self.assertIsNotNone(notion_page)
        NotionWriter.handle_page(notion_page)

    def test_write_posts_with_hexo_channel(self):
        Config.set_channels(['Hexo'])
        Config.set_page_titles_match([
            "^(Hexo page -)"
        ])
        NotionWriter.clean_output()

        notion_pages = NotionReader.handle_post()
        self.assertIsNotNone(notion_pages)

        for notion_page in notion_pages:
            NotionWriter.handle_page(notion_page)


