import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notion_page import NotionPage
from notion_reader import NotionReader
from config import Config

class TestMigration(unittest.TestCase):

    def setUp(self):
        Config.set('notion_token', 'secret_test')
        Config.set('blog_url', 'https://www.notion.so/test-page-1234567890abcdef1234567890abcdef')
        Config.set('page_titles', ['all'])
        Config.set('page_titles_match', [])
        
        # Manually define getters since we are not calling Config.parse_configs()
        Config.define_getter('notion_token')
        Config.define_getter('blog_url')
        Config.define_getter('page_titles')
        Config.define_getter('page_titles_match')
        Config.define_getter('download_image')
        Config.set('download_image', False)

    @patch('notion_page.Client')
    @patch('notion_reader.Client')
    def test_notion_reader_handle_post(self, mock_reader_client_cls, mock_page_client_cls):
        # Mock Client instance
        mock_client = MagicMock()
        mock_reader_client_cls.return_value = mock_client
        mock_page_client_cls.return_value = mock_client

        # Mock pages.retrieve for main page
        mock_client.pages.retrieve.return_value = {
            'id': '12345678-90ab-cdef-1234-567890abcdef',
            'object': 'page',
            'properties': {
                'title': {
                    'type': 'title',
                    'title': [{'plain_text': 'Main Page'}]
                }
            }
        }

        # Mock blocks.children.list for main page (returns a subpage)
        mock_client.blocks.children.list.return_value = {
            'results': [
                {
                    'id': 'subpage-id',
                    'type': 'child_page',
                    'child_page': {'title': 'Sub Page'}
                }
            ],
            'has_more': False
        }

        # Mock pages.retrieve for subpage
        def side_effect_pages_retrieve(page_id):
            if page_id == '12345678-90ab-cdef-1234-567890abcdef':
                return {
                    'id': '12345678-90ab-cdef-1234-567890abcdef',
                    'object': 'page',
                    'properties': {'title': {'type': 'title', 'title': [{'plain_text': 'Main Page'}]}}
                }
            if page_id == 'subpage-id':
                return {
                    'id': 'subpage-id',
                    'object': 'page',
                    'properties': {'title': {'type': 'title', 'title': [{'plain_text': 'Sub Page'}]}}
                }
            return {}
        
        mock_client.pages.retrieve.side_effect = side_effect_pages_retrieve

        # Mock blocks.children.list for subpage (returns some content)
        def side_effect_blocks_children(block_id, start_cursor=None):
            if block_id == '12345678-90ab-cdef-1234-567890abcdef':
                 return {
                    'results': [
                        {
                            'id': 'subpage-id',
                            'type': 'child_page',
                            'child_page': {'title': 'Sub Page'}
                        }
                    ],
                    'has_more': False
                }
            if block_id == 'subpage-id':
                return {
                    'results': [
                        {
                            'id': 'block-1',
                            'type': 'paragraph',
                            'paragraph': {
                                'rich_text': [{'plain_text': 'Hello World'}]
                            }
                        }
                    ],
                    'has_more': False
                }
            return {'results': [], 'has_more': False}

        mock_client.blocks.children.list.side_effect = side_effect_blocks_children

        # Run NotionReader
        pages = NotionReader.handle_post()
        
        # Verify
        self.assertEqual(len(pages), 2) # Main page + Sub page
        self.assertEqual(pages[0].title, 'Main Page')
        self.assertEqual(pages[1].title, 'Sub Page')
        
        # Verify content of subpage
        subpage = pages[1]
        self.assertEqual(len(subpage.blocks), 1)
        self.assertEqual(subpage.blocks[0].type, 'text')
        self.assertEqual(subpage.blocks[0].text, 'Hello World')

    @patch('notion_page.Client')
    def test_notion_page_parse(self, mock_client_cls):
        # Mock Client for NotionPage internal calls
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        page_data = {
            'id': 'page-id',
            'object': 'page',
            'properties': {
                'title': {
                    'type': 'title',
                    'title': [{'plain_text': 'Test Page'}]
                }
            }
        }

        # Mock blocks.children.list
        mock_client.blocks.children.list.return_value = {
            'results': [
                {
                    'id': 'block-1',
                    'type': 'heading_1',
                    'heading_1': {'rich_text': [{'plain_text': 'Header 1'}]}
                },
                {
                    'id': 'block-2',
                    'type': 'bulleted_list_item',
                    'bulleted_list_item': {'rich_text': [{'plain_text': 'Item 1'}]},
                    'has_children': False
                }
            ],
            'has_more': False
        }

        page = NotionPage()
        page.parse(page_data)

        self.assertEqual(page.title, 'Test Page')
        self.assertEqual(len(page.blocks), 2)
        self.assertEqual(page.blocks[0].type, 'header')
        self.assertEqual(page.blocks[0].text, 'Header 1')
        self.assertEqual(page.blocks[1].type, 'bulleted_list')
        self.assertEqual(page.blocks[1].text, 'Item 1')

if __name__ == '__main__':
    unittest.main()
