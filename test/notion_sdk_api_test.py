import os
import unittest
from pprint import pprint

from notion_client import Client

from utils.utils import Utils


class NotionCiTest(unittest.TestCase):

    def setUp(self):
        if not Utils.check_module_installed("notion-client"):
            raise Exception('Install notion client first: pip install notion-client')
        self.notion = Client(auth=os.environ["NOTION_TOKEN"])

    def test_get_users(self):
        list_users_response = self.notion.users.list()
        pprint(list_users_response)
        self.assertIsNotNone(list_users_response)
        self.assertEqual('list', list_users_response['object'])
        users = list_users_response['results']
        self.assertTrue(len(users) >= 0)
        pass

    def test_search_data_base(self):
        search_database = self.notion.search(filter={"property": "object", "value": "database"})
        pprint(search_database)
        self.assertIsNotNone(search_database)
        pass

    def test_search_page(self):
        search_database = self.notion.search(filter={"property": "object", "value": "page"})
        pprint(search_database)
        self.assertIsNotNone(search_database)
        pass
