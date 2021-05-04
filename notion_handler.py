from notion.client import NotionClient

from config import Config
from notion_page import NotionPage
from notion.client import NotionClient

from config import Config
from notion_page import NotionPage

NOTION_CLIENT = None


class NotionHandler:

    @staticmethod
    def get_client() -> NotionClient:
        global NOTION_CLIENT
        if not NOTION_CLIENT:
            NOTION_CLIENT = NotionClient(token_v2=Config.token_v2())
        return NOTION_CLIENT

    @staticmethod
    def handle_post():
        main_page = NotionHandler.get_client().get_block(Config.blog_url())
        notion_pages = []
        NotionHandler.recurse_handle_page(notion_pages, main_page)
        NotionHandler.on_handle_notion_pages(notion_pages)
        return notion_pages

    @staticmethod
    def recurse_handle_page(notion_pages, page):
        notion_page = NotionPage()
        notion_page.parse(page)
        NotionHandler.on_handle_notion_page(notion_page)
        notion_pages.append(notion_page)

        if page.children:
            for subpage in page.children:
                if subpage.type == 'page':
                    NotionHandler.recurse_handle_page(notion_pages, subpage)

        pass

    @staticmethod
    def on_handle_notion_page(notion_page):
        pass

    @staticmethod
    def on_handle_notion_pages(notion_pages):
        pass


