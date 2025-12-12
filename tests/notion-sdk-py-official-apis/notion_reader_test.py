import os
import unittest

from config import Config
from notion_page import PageTextBlock, NotionPage, PageTocBlock, PageTableBlock, \
    PageSyncedSourceBlock, PageSyncedCopyBlock
from notion_reader import NotionReader
from utils.utils import Utils


class NotionHandlerTest(unittest.TestCase):

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

    def test_check_token(self):
        self.assertTrue("NOTION_TOKEN_V2" in os.environ, "Token exist")

    def test_handle_post(self):
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

    def test_parse_text_block_with_obfuscated_links(self):
        block = PageTextBlock()
        block.text = '''
        ## Link Obfuscating
        [This is a link](https://respawn.io)
        [This is also a link](https://www.notion.so/kaedea/NotionDown-Obfusing-Blocks-25959a72e55041d6aed69f90226fa45c)
        [This is an obfuscated link]([https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4](https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4))
        ## Image Obfuscating
        ![This is image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T162928Z&X-Amz-Expires=86400&X-Amz-Signature=ae28a9fbf4beb4cf82bf1438c9cbd9f18e2d882aa33874a94bac6cdea09f3f1f&X-Amz-SignedHeaders=host)
        ![This is also an image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host)
        ![This is an obfuscated image]([https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host))
        '''

        block_text = block.write_block()
        print(block_text)

        self.assertEqual('''
        ## Link Obfuscating
        [This is a link](https://respawn.io)
        [This is also a link](https://www.notion.so/kaedea/NotionDown-Obfusing-Blocks-25959a72e55041d6aed69f90226fa45c)
        [This is an obfuscated link](https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4)
        ## Image Obfuscating
        ![This is image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T162928Z&X-Amz-Expires=86400&X-Amz-Signature=ae28a9fbf4beb4cf82bf1438c9cbd9f18e2d882aa33874a94bac6cdea09f3f1f&X-Amz-SignedHeaders=host)
        ![This is also an image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host)
        ![This is an obfuscated image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host)
        ''', block_text)

    def test_parse_notion_page_with_channel_short_code(self):
        test_page = NotionReader.read_page_with_title("NotionDown ShortCode")
        self.assertIsNotNone(test_page)

        notion_page = NotionPage()
        notion_page.parse(test_page)
        self.assertIsNotNone(notion_page)

    def test_parse_notion_page_with_pull_quote(self):
        test_page = NotionReader.read_page_with_title("NotionDown Pullquote Blocks")
        self.assertIsNotNone(test_page)

        notion_page = NotionPage()
        notion_page.parse(test_page)
        self.assertIsNotNone(notion_page)

    def test_parse_notion_page_with_toc(self):
        test_page = NotionReader.read_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(test_page)

        notion_page = NotionPage()
        notion_page.parse(test_page)
        page_toc_block: PageTocBlock = Utils.find_one(notion_page.blocks, lambda it: type(it) == PageTocBlock)

        self.assertIsNotNone(page_toc_block)
        text = page_toc_block.write_block()
        self.assertTrue(len(text.strip()) > 0)

    def test_parse_notion_page_with_table(self):
        test_page = NotionReader.read_page_with_title("NotionDown Table")
        self.assertIsNotNone(test_page)

        notion_page = NotionPage()
        notion_page.parse(test_page)
        page_table_block: PageTableBlock = Utils.find_one(notion_page.blocks, lambda it: type(it) == PageTableBlock)

        self.assertIsNotNone(page_table_block)
        text = page_table_block.write_block()
        self.assertTrue(len(text.strip()) > 0)

    def test_parse_notion_page_with_synced_block(self):
        test_page = NotionReader.read_page_with_title("NotionDown Synchronic Block")
        self.assertIsNotNone(test_page)

        notion_page = NotionPage()
        notion_page.parse(test_page)

        page_block: PageSyncedSourceBlock = Utils.find_one(notion_page.blocks, lambda it: type(it) == PageSyncedSourceBlock)
        self.assertIsNotNone(page_block)
        text = page_block.write_block()
        self.assertTrue(len(text.strip()) > 0)

        page_block: PageSyncedCopyBlock = Utils.find_one(notion_page.blocks, lambda it: type(it) == PageSyncedCopyBlock)
        self.assertIsNotNone(page_block)
        text = page_block.write_block()
        self.assertTrue(len(text.strip()) > 0)

    def test_read_notion_page_with_hexo(self):
        Config.set_page_titles_match([
            "^(Hexo page -)"
        ])
        test_pages = NotionReader.read_all_pages()
        self.assertTrue(len(test_pages) > 0)

    def test_filter_descendants(self):
        # Mock pages
        root = {'id': 'root', 'parent': {'type': 'workspace'}}
        child1 = {'id': 'c1', 'parent': {'type': 'page_id', 'page_id': 'root'}}
        child2 = {'id': 'c2', 'parent': {'type': 'page_id', 'page_id': 'root'}}
        grandchild1 = {'id': 'gc1', 'parent': {'type': 'page_id', 'page_id': 'c1'}}
        outsider = {'id': 'other', 'parent': {'type': 'workspace'}}
        outsider_child = {'id': 'oc1', 'parent': {'type': 'page_id', 'page_id': 'other'}}
        
        all_pages = [root, child1, child2, grandchild1, outsider, outsider_child]
        
        # Test filtering
        descendants = NotionReader._filter_descendants(all_pages, 'root')
        ids = [p['id'] for p in descendants]
        
        self.assertIn('root', ids)
        self.assertIn('c1', ids)
        self.assertIn('c2', ids)
        self.assertIn('gc1', ids)
        self.assertNotIn('other', ids)
        self.assertNotIn('oc1', ids)
        self.assertEqual(len(ids), 4)

