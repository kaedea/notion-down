import re
import typing

from utils.utils import Utils

if not Utils.check_module_installed("notion"):
    raise Exception("Pls call 'pip install notion' first!")

from typing import List
from notion.block import PageBlock
from notion.client import NotionClient
from config import Config
from notion_page import NotionPage

NOTION_CLIENT = None


class NotionReader:

    @staticmethod
    def get_client() -> NotionClient:
        global NOTION_CLIENT
        if not NOTION_CLIENT:
            NOTION_CLIENT = NotionClient(token_v2=Config.token_v2())
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
        find_one = Utils.find_one(pages, lambda it: it.title == page_title)
        if not find_one:
            return None
        return NotionReader._parse_page(find_one)

    @staticmethod
    def handle_page(page) -> NotionPage:
        print("#handle_single_page")
        return NotionReader._parse_page(page)

    @staticmethod
    def read_main_page() -> typing.Optional[PageBlock]:
        print("#read_main_page")
        return NotionReader.get_client().get_block(Config.blog_url())

    @staticmethod
    def read_all_pages() -> typing.List[PageBlock]:
        print("#read_all_pages")
        return NotionReader._read_post_pages()

    @staticmethod
    def read_page_with_title(page_title: str) -> typing.Optional[PageBlock]:
        print("#read_page_with_title")
        return Utils.find_one(NotionReader.read_all_pages(), lambda it: it.title == page_title)

    @staticmethod
    def _read_post_pages() -> typing.List[PageBlock]:
        # get all pages
        main_page = NotionReader.read_main_page()
        page_blocks = []
        NotionReader._recurse_read_page(page_blocks, main_page)

        # filter by config
        titles = Config.page_titles()
        titles_match = Config.page_titles_match()
        if titles == ['all'] and len(titles_match) == 0:
            return page_blocks

        filter_by_titles = [it for it in page_blocks if it.title in titles]
        filter_by_titles_match = [it for it in page_blocks if Utils.find_one(
            titles_match,
            lambda match: re.compile(match).match(it.title)
        )]
        filter_by_titles.extend([it for it in filter_by_titles_match if it not in filter_by_titles])
        return filter_by_titles

    @staticmethod
    def _recurse_read_page(page_blocks: typing.List[PageBlock], page: PageBlock):
        if page and page.type == 'page':
            page_blocks.append(page)

        if page.children:
            for subpage in page.children:
                if subpage.type == 'page':
                    NotionReader._recurse_read_page(page_blocks, subpage)

        pass

    @staticmethod
    def _parse_page(page: PageBlock) -> NotionPage:
        print("parse page, id = " + page.id)
        notion_page = NotionPage()
        notion_page.parse(page)
        return notion_page




