import json
import os
import shutil
import typing
import urllib
from pathlib import Path

from config import Config
from notion_page import NotionPage, PageBaseBlock


class NotionWriter:

    @staticmethod
    def clean_output():
        output_dir = Path(Config.output())
        shutil.rmtree(output_dir)
        output_dir.mkdir()

    # noinspection SpellCheckingInspection
    @staticmethod
    def handle_page(notion_page: NotionPage):
        if not notion_page.is_markdown_able():
            print("Skip non-markdownable page: " + notion_page.get_identify())
            return
        if not notion_page.is_output_able():
            print("Skip non-outputable page: " + notion_page.get_identify())
            return

        print("Write page: " + notion_page.get_identify())
        page_writer = NotionPageWriter()
        page_writer.write_page(notion_page)
        print("\n----------\n")


# noinspection PyMethodMayBeStatic
class NotionPageWriter:
    def __init__(self):
        self.root_dir = "NotionDown"
        self.assets_dir = "assets"
        self.post_dir = "post"
        self.draft_dir = "draft"

    def write_page(self, notion_page: NotionPage):
        print("#write_page")
        print("page identify = " + notion_page.get_identify())

        page_lines = self._start_writing(notion_page)
        self._on_dump_page_content(page_lines)

        file_path = self._configure_file_path(notion_page)
        self._prepare_file(file_path)
        self._write_file("\n".join(page_lines), file_path)

        properties_file_path = file_path + "_properties.json"
        self._prepare_file(properties_file_path)
        self._write_file(json.dumps(notion_page.properties, indent=2), properties_file_path)
        pass

    def _start_writing(self, notion_page: NotionPage) -> typing.List[typing.Text]:
        page_lines = []
        self._write_header(page_lines, notion_page)
        self._write_blocks(page_lines, notion_page.blocks)
        self._write_tail(page_lines, notion_page)
        return page_lines

    def _write_header(self, page_lines: typing.List[typing.Text], notion_page: NotionPage):
        page_lines.append("")
        pass

    def _write_blocks(self, page_lines: typing.List[typing.Text], blocks: typing.List[PageBaseBlock]):
        for block in blocks:
            self._write_block(page_lines, block)
            page_lines.append("")
        pass

    def _write_block(self, page_lines: typing.List[typing.Text], block: PageBaseBlock):
        page_lines.append(block.write_block())
        pass

    def _write_tail(self, page_lines: typing.List[typing.Text], notion_page: NotionPage):
        page_lines.append("\n")
        page_lines.append("""
<!-- NotionPageWriter
-->""")
        pass

    def _on_dump_page_content(self, page_lines):
        pass

    def _configure_file_path(self, notion_page: NotionPage) -> typing.Text:
        print("#_configure_file_path")

        base_dir = os.path.join(
            Config.output(),
            self.root_dir + "/" + (self.post_dir if notion_page.is_published() else self.draft_dir)
        )
        Path(base_dir).mkdir(parents=True, exist_ok=True)

        target_path = os.path.join(
            notion_page.get_file_dir() if notion_page.get_file_dir() else "",
            urllib.parse.quote_plus(notion_page.get_file_name())
        )

        file_path = os.path.join(base_dir, target_path + ".md")
        print("file_path = " + file_path)
        return file_path

    def _prepare_file(self, file_path):
        if os.path.exists(file_path):
            if not Config.debuggable():
                raise Exception("file already exists: " + file_path)
        else:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        pass

    def _write_file(self, content, file_path):
        with open(file_path, "w+") as f:
            f.write(content)
