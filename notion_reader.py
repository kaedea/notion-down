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
    def read_main_page() -> PageBlock:
        return NotionReader.get_client().get_block(Config.blog_url())

    @staticmethod
    def handle_post() -> List[NotionPage]:
        print("#handle_post")
        main_page = NotionReader.read_main_page()
        notion_pages = []
        NotionReader._recurse_handle_page(notion_pages, main_page)
        NotionReader.on_handle_notion_pages(notion_pages)
        print("Done\n\n")
        return notion_pages

    @staticmethod
    def _recurse_handle_page(notion_pages, page: PageBlock):
        print("parse page, id = " + page.id)
        notion_page = NotionPage()
        notion_page.parse(page)
        NotionReader.on_handle_notion_page(notion_page)
        notion_pages.append(notion_page)

        if page.children:
            for subpage in page.children:
                if subpage.type == 'page':
                    NotionReader._recurse_handle_page(notion_pages, subpage)

        pass

    @staticmethod
    def handle_single_page(page) -> NotionPage:
        print("#handle_single_page")
        print("parse page, id = " + page.id)
        notion_page = NotionPage()
        notion_page.parse(page)
        NotionReader.on_handle_notion_page(notion_page)
        print("Done\n\n")
        return notion_page

    @staticmethod
    def on_handle_notion_page(notion_page):
        pass

    @staticmethod
    def on_handle_notion_pages(notion_pages):
        pass


