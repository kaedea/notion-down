import os
import unittest

from config import Config
from corrects.inspect_spell import PyCorrectorInspector
from notion_page import NotionPage
from notion_reader import NotionReader
from notion_writer import NotionWriter, SpellInspectWriter
from utils.utils import Utils


class CorrectsApiTest(unittest.TestCase):

    def test_issue_format(self):
        text = '真麻烦你了。希望你们好好的跳无。少先队员因该为老人让坐。机七学习是人工智能领遇最能体现智能的一个分知。一只小鱼船浮在平净的河面上。我的家乡是有明的渔米之乡。'
        issues = [
            ['无', '舞', 14, 15],
            ['因该', '应该', 20, 22],
            ['坐', '座', 26, 27],
            ['机七', '机器', 28, 30],
            ['领遇', '领域', 37, 39],
            ['平净', '平静', 58, 60],
            ['有明', '有名', 70, 72]
        ]
        formatted_text = SpellInspectWriter._format_text_with_inspect_issues(text, issues)
        self.assertEquals(
            '真麻烦你了。希望你们好好的跳~~无~~。少先队员~~因该~~为老人让~~坐~~。~~机七~~学习是人工智能~~领遇~~最能体现智能的一个分知。一只小鱼船浮在~~平净~~的河面上。我的家乡是~~有明~~的渔米之乡。',
            formatted_text
        )

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

    def _get_test_pages(self) -> NotionPage:
        Config.load_env()
        Config.set_debuggable(True)
        Config.set_blog_url(
            "https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))

        main_page = NotionReader.read_main_page()
        self.assertIsNotNone(main_page)
        test_pages = Utils.find(
            main_page.children,
            lambda it: it and str(it.title) in [
                "NotionDown Spelling Inspect",
                "MarkDown Test Page - SPA",
                "MarkDown Test Page - NotionDown",
            ]
        )

        md_pages = []
        for test_page in test_pages:
            self.assertIsNotNone(test_page)
            md_page = NotionReader.handle_single_page(test_page)
            self.assertIsNotNone(md_page)
            self.assertTrue(
                "should have test text block",
                len([it for it in md_page.blocks if it.type == 'text']) > 0
            )
            md_pages.append(md_page)

        return md_pages

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

    def test_pycorrector_spelling_inspect_writer(self):
        md_page = self._get_test_page()
        Config.set_channels(['SpellInspect'])
        NotionWriter.clean_output()
        NotionWriter.handle_page(md_page)

    def test_pycorrector_spelling_inspect_writer_r2(self):
        md_pages = self._get_test_pages()
        Config.set_channels(['SpellInspect'])
        NotionWriter.clean_output()
        NotionWriter.inspect_pages(md_pages)
