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


    def test_parse_blog_pages(self):
        # Config.set_download_image(True)
        Config.set_writer('Hexo')
        Config.set_channels(['default'])
        NotionWriter.clean_output()
        md_pages = NotionReader.handle_post()
        self.assertIsNotNone(md_pages)

        for md_page in md_pages:
            self.assertIsNotNone(md_page)
            NotionWriter.handle_page(md_page)
            pass

    def test_parse_blog_page_1(self):
        # Config.set_download_image(True)
        Config.set_writer('Hexo')
        Config.set_channels(['default'])
        NotionWriter.clean_output()
        md_page = NotionReader.handle_page_with_title("增量静态检查（SPA）在代码合入检查里的应用")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_parse_blog_page_2(self):
        # Config.set_download_image(True)
        Config.set_writer('Hexo')
        Config.set_channels(['default', 'WXG'])
        NotionWriter.clean_output()
        md_page = NotionReader.handle_page_with_title("一种 Android 应用内全局获取 Context 实例的装置")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_parse_blog_page_3(self):
        NotionWriter.clean_output()
        md_page = NotionReader.handle_page_with_title("Copy of Resume")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass


