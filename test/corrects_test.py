import os
import unittest

from config import Config
from corrects.inspect_spell import PyCorrectorInspector
from notion_page import NotionPage
from notion_reader import NotionReader
from notion_writer import NotionWriter
from utils.utils import Utils


class CorrectsApiTest(unittest.TestCase):

    def _get_test_page(self) -> NotionPage:
        Config.load_env()
        Config.set_debuggable(True)
        Config.set_blog_url(
            "https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        main_page = NotionReader.read_main_page()
        self.assertIsNotNone(main_page)
        test_page = Utils.find_one(
            main_page.children,
            lambda it: it and str(it.title) == "NotionDown Spelling Inspect"
        )
        self.assertIsNotNone(test_page)
        md_page = NotionReader.handle_single_page(test_page)
        self.assertIsNotNone(md_page)
        self.assertTrue(
            "should have test text block",
            len([it for it in md_page.blocks if it.type == 'text']) > 0
        )
        return md_page

    def test_read_demo_page(self):
        self._get_test_page()

    def test_pycorrector_spelling_inspect(self):
        md_page = self._get_test_page()
        for block in md_page.blocks:
            text = block.write_block()
            if text:
                print("inspect bgn: {}".format(text))
                PyCorrectorInspector().inspect_text(text)
            else:
                print("inspect skip: {}".format(text))

            print("------")

    def test_pycorrector_spelling_inspect_witter(self):
        md_page = self._get_test_page()
        NotionWriter.inspect_page(md_page)
