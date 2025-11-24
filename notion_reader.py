import re
import typing
from typing import List, Optional, Any

from notion_client import Client
from config import Config
from notion_page import NotionPage
from utils.utils import Utils

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
        # Note: page is now a dict, so we access title differently or wrap it
        # For now assuming we adapt _parse_page to handle the dict
        find_one = Utils.find_one(pages, lambda it: NotionReader._get_page_title(it) == page_title)
        if not find_one:
            return None
        return NotionReader._parse_page(find_one)

    @staticmethod
    def handle_page(page) -> NotionPage:
        print("#handle_single_page")
        return NotionReader._parse_page(page)

    @staticmethod
    def read_main_page() -> Any:
        print("#read_main_page")
        try:
            page_id = NotionReader._extract_id(Config.blog_url())
            return NotionReader.get_client().blocks.retrieve(page_id)
        except Exception as e:
            raise e

    @staticmethod
    def read_all_pages() -> typing.List[Any]:
        print("#read_all_pages")
        return NotionReader._read_post_pages()

    @staticmethod
    def read_page_with_title(page_title: str) -> typing.Optional[Any]:
        print("#read_page_with_title")
        return Utils.find_one(NotionReader.read_all_pages(), lambda it: NotionReader._get_page_title(it) == page_title)

    @staticmethod
    def _read_post_pages() -> typing.List[Any]:
        # get all pages
        main_page = NotionReader.read_main_page()
        page_blocks = []
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
    def _recurse_read_page(page_blocks: typing.List[Any], page: Any):
        # In official API, 'child_page' is the type for a page block inside another page
        # But the retrieved block itself has a type.
        # If we retrieved a page, it might be a 'page' object (from database) or a block with type 'child_page'.
        
        # When using blocks.retrieve, we get a block object.
        # If it's a page, it usually has type 'child_page' if it's inside another page.
        # But the top level page might just be a block.
        
        # We need to fetch children to find subpages.
        
        if 'type' in page and page['type'] == 'child_page':
             page_blocks.append(page)
        elif page['object'] == 'page': # Top level page from databases.retrieve or similar
             page_blocks.append(page)
        elif page['object'] == 'block' and page['type'] == 'child_page':
             page_blocks.append(page)
        
        # Fetch children
        try:
            children = NotionReader.get_client().blocks.children.list(block_id=page['id'])
            for sub_block in children.get('results', []):
                if sub_block['type'] == 'child_page':
                    NotionReader._recurse_read_page(page_blocks, sub_block)
        except Exception as e:
            print(f"Error fetching children for {page['id']}: {e}")

    @staticmethod
    def _parse_page(page: Any) -> NotionPage:
        print("parse page, id = " + page['id'])
        notion_page = NotionPage()
        notion_page.parse(page)
        return notion_page

    @staticmethod
    def _extract_id(url_or_id: str) -> str:
        # Simple extraction: if it looks like a URL, extract the last part.
        # If it's a 32 char hex string, it's an ID.
        match = re.search(r'([a-f0-9]{32})', url_or_id)
        if match:
            return match.group(1)
        return url_or_id

    @staticmethod
    def _get_page_title(page: Any) -> str:
        if 'child_page' in page:
            return page['child_page']['title']
        # Handle other cases if necessary (e.g. database page properties)
        # For now assuming child_page structure for pages in a page
        if 'properties' in page:
             # This is tricky as it depends on the property name for title
             # Usually 'Name' or 'title'
             for prop in page['properties'].values():
                 if prop['id'] == 'title':
                     if prop['title']:
                         return prop['title'][0]['plain_text']
                     return ""
        return ""





