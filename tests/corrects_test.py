import os
import typing
import unittest

from config import Config
from notion_page import NotionPage
from notion_reader import NotionReader
from notion_writer import NotionWriter, SpellInspectWriter
from utils.utils import Utils


class CorrectsApiTest(unittest.TestCase):

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

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
        md_page = NotionReader.handle_page_with_title("NotionDown Spelling Inspect")
        self.assertIsNotNone(md_page)
        self.assertTrue(
            "should have test text block",
            len([it for it in md_page.blocks if it.type == 'text']) > 0
        )
        return md_page

    def _get_test_pages(self) -> typing.List[NotionPage]:
        Config.set_page_titles([
            "NotionDown Spelling Inspect",
            "MarkDown Test Page - SPA",
            "MarkDown Test Page - NotionDown",
        ])

        md_pages = NotionReader.handle_post()
        self.assertTrue(len(md_pages) > 0)
        for md_page in md_pages:
            self.assertTrue(
                "should have test text block",
                len([it for it in md_page.blocks if it.type == 'text']) > 0
            )
        return md_pages

    def test_read_demo_page(self):
        self.assertIsNotNone(self._get_test_page())
        self.assertTrue(len(self._get_test_pages()) > 1)

    def test_pycorrector_spelling_inspect(self):
        md_page = self._get_test_page()
        for block in md_page.blocks:
            text = block.write_block()
            if text:
                print("inspect bgn: {}".format(text))
                from corrects.inspect_spell import PyCorrectorInspector
                PyCorrectorInspector().inspect_text(text)
            else:
                print("inspect skip: {}".format(text))

            print("------")

    def test_pycorrector_spelling_inspect_writer(self):
        md_page = self._get_test_page()
        Config.set_writer(['SpellInspect'])
        NotionWriter.clean_output()
        NotionWriter.handle_page(md_page)

    def test_pycorrector_spelling_inspect_writer_r2(self):
        md_pages = self._get_test_pages()
        Config.set_writer(['SpellInspect'])
        NotionWriter.clean_output()
        NotionWriter.handle_pages(md_pages)
