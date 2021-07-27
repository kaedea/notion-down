import os
import unittest

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils


class NotionBlogParseTest(unittest.TestCase):

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.set_blog_url('https://www.notion.so/Android-0fa32fcec416498da779f91166f0a0f5')
        Config.check_required_args()

    def test_parse_blog_page(self):
        # Config.set_download_image(True)
        Config.set_channels(['default'])
        NotionWriter.clean_output()
        md_page = NotionReader.handle_page_with_title("Android App 电量统计原理与优化")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

