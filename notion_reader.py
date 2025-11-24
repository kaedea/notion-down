import re
import typing
from typing import List, Dict, Any

from notion_client import Client
from config import Config
from notion_page import NotionPage
from utils.utils import Utils
from utils.notion_utils import NotionUtils

if not Utils.check_module_installed("notion_client"):
    raise Exception("Pls call 'pip install notion-client' first!")

NOTION_CLIENT = None


class NotionReader:

    @staticmethod
    def get_client() -> Client:
        global NOTION_CLIENT
        if not NOTION_CLIENT:
            if not Config.notion_token():
                raise Exception('notion_token should be presented!')

            NOTION_CLIENT = Client(auth=Config.notion_token())
        return NOTION_CLIENT

    @staticmethod
    def handle_post() -> List[NotionPage]:
        print("#handle_post")
        print("read all pages from main page")
        page_blocks = NotionReader._read_post_pages()

        print("parse all pages")
        notion_pages = []
        for page in page_blocks:
            notion_pages.append(NotionReader._parse_page(page))

        print("Done\n\n")
        return notion_pages

    @staticmethod
    def handle_page_with_title(page_title: str) -> typing.Optional[NotionPage]:
        print("#handle_page_with_title: " + page_title)
        pages = NotionReader._read_post_pages()
        # Note: Official API pages have 'properties' -> 'title' -> 'title' -> 'plain_text'
        # But here 'pages' are likely Block objects or Page objects.
        # We need to ensure we are filtering correctly.
        # For now, assuming _read_post_pages returns a list of Page objects (dicts).
        
        find_one = Utils.find_one(pages, lambda it: NotionReader._get_page_title(it) == page_title)
        if not find_one:
            return None
        return NotionReader._parse_page(find_one)

    @staticmethod
    def handle_page(page) -> NotionPage:
        print("#handle_single_page")
        return NotionReader._parse_page(page)

    @staticmethod
    def read_main_page() -> Dict[str, Any]:
        print("#read_main_page")
        try:
            page_id = NotionUtils.extract_id(Config.blog_url())
            return NotionReader.get_client().pages.retrieve(page_id=page_id)
        except Exception as e:
            raise e

    @staticmethod
    def read_all_pages() -> typing.List[Dict[str, Any]]:
        print("#read_all_pages")
        return NotionReader._read_post_pages()

    @staticmethod
    def read_page_with_title(page_title: str) -> typing.Optional[Dict[str, Any]]:
        print("#read_page_with_title")
        return Utils.find_one(NotionReader.read_all_pages(), lambda it: NotionReader._get_page_title(it) == page_title)

    @staticmethod
    def _read_post_pages() -> typing.List[Dict[str, Any]]:
        # get all pages
        main_page = NotionReader.read_main_page()
        page_blocks = []
        
        # In official API, we need to list children of the main page to find sub-pages
        NotionReader._recurse_read_page(page_blocks, main_page)

        # filter by config
        titles = Config.page_titles()
        titles_match = Config.page_titles_match()
        if titles == ['all'] and (not titles_match or len(titles_match) == 0):
            return page_blocks

        filter_by_titles = [it for it in page_blocks if NotionReader._get_page_title(it) in titles]
        filter_by_titles_match = [it for it in page_blocks if Utils.find_one(
            titles_match,
            lambda match: re.compile(match).match(NotionReader._get_page_title(it))
        )]
        filter_by_titles.extend([it for it in filter_by_titles_match if it not in filter_by_titles])
        return filter_by_titles

    @staticmethod
    def _recurse_read_page(page_blocks: typing.List[Dict[str, Any]], parent_page: Dict[str, Any]):
        # Add the current page if it's a page (and not the root if we only want children, but logic seems to include root or subpages)
        # The original logic seemed to flatten the tree.
        
        if parent_page.get('object') == 'page':
             page_blocks.append(parent_page)

        # Get children
        # Official API: list children blocks. If a child is a child_page, it's a subpage.
        # Note: 'pages' in Notion are blocks of type 'child_page' when inside another page.
        # But to get the full Page object (with properties), we might need to retrieve it separately 
        # OR just use the block if it has enough info. 
        # However, 'child_page' block doesn't have properties like 'Date', 'Tags' etc.
        # So we MUST retrieve the page object for each 'child_page' block.
        
        parent_id = parent_page.get('id')
        children = NotionReader._get_children(parent_id)
        
        for child in children:
            if child.get('type') == 'child_page':
                # It's a subpage. Retrieve the full page details.
                try:
                    child_page_details = NotionReader.get_client().pages.retrieve(child.get('id'))
                    NotionReader._recurse_read_page(page_blocks, child_page_details)
                except Exception as e:
                    print(f"Error retrieving subpage {child.get('id')}: {e}")

    @staticmethod
    def _get_children(block_id: str) -> List[Dict[str, Any]]:
        children = []
        has_more = True
        start_cursor = None
        
        while has_more:
            response = NotionReader.get_client().blocks.children.list(
                block_id=block_id,
                start_cursor=start_cursor
            )
            children.extend(response.get('results', []))
            has_more = response.get('has_more')
            start_cursor = response.get('next_cursor')
            
        return children

    @staticmethod
    def _parse_page(page: Dict[str, Any]) -> NotionPage:
        print("parse page, id = " + page.get('id'))
        notion_page = NotionPage()
        notion_page.parse(page)
        return notion_page

    @staticmethod
    def _get_page_title(page: Dict[str, Any]) -> str:
        properties = page.get('properties', {})
        # Title property name varies, but usually it's 'title' type
        for prop_name, prop_val in properties.items():
            if prop_val.get('type') == 'title':
                return NotionUtils.get_plain_text(prop_val.get('title', []))
        return ""




