import json
import os
from pathlib import Path

import requests
import typing

from notion.utils import slugify

from config import Config
from notion_page import NotionPage, PageBaseBlock, PageImageBlock, PageBlockJoiner
from utils.utils import FileUtils, Utils


class NotionOutput:

    def __init__(self) -> None:
        self.channel = ""


class NotionDirOutput(NotionOutput):

    def __init__(self) -> None:
        super().__init__()
        self.output_dir = ""

    def has_output(self):
        return self.output_dir and FileUtils.exists(self.output_dir)

    def __str__(self) -> str:
        return json.dumps({
            "channel": self.channel,
            "output_dir": self.output_dir,
        }, indent=2)


class NotionFileOutput(NotionDirOutput):

    def __init__(self) -> None:
        super().__init__()
        self.markdown_path = ""
        self.properties_path = ""

    def has_markdown(self):
        return self.markdown_path and FileUtils.exists(self.markdown_path)

    def has_properties(self):
        return self.properties_path and FileUtils.exists(self.properties_path)

    def __str__(self) -> str:
        return json.dumps({
            "channel": self.channel,
            "output_dir": self.output_dir,
            "markdown_path": self.markdown_path,
            "properties_path": self.properties_path,
        }, indent=2)


class NotionWriter:

    @staticmethod
    def get_page_writer(writer=None):
        if not writer or str(writer).lower() == "notion":
            return NotionPageWriter()

        if str(writer).lower() == "spellinspect":
            return SpellInspectWriter()
        if str(writer).lower() == "hexo":
            return HexoWriter()
        return ChannelWriter(writer)

    @staticmethod
    def clean_output():
        FileUtils.clean_dir(Config.output())

    # noinspection SpellCheckingInspection
    @staticmethod
    def handle_page(notion_page: NotionPage) -> typing.Dict[str, NotionFileOutput]:
        print("Write page: " + notion_page.get_identify())
        if not Config.writer():
            page_writer = NotionWriter.get_page_writer()
            if not page_writer.is_markdown_able(notion_page):
                print("Skip non-markdownable page: " + notion_page.get_identify())
                return {}
            if not page_writer.is_output_able(notion_page):
                print("Skip non-outputable page: " + notion_page.get_identify())
                return {}

            output = page_writer.write_page(notion_page)
            print("\n----------\n")
            return {
                "default": output
            }

        else:
            outputs = {}
            # FIXME: fix return structure
            for writer in [Config.writer()]:
                page_writer = NotionWriter.get_page_writer(writer)
                if not page_writer.is_markdown_able(notion_page):
                    print("Skip non-markdownable page: " + notion_page.get_identify())
                    outputs[writer] = {}
                    continue
                if not page_writer.is_output_able(notion_page):
                    print("Skip non-outputable page: " + notion_page.get_identify())
                    outputs[writer] = {}
                    continue

                output = page_writer.write_page(notion_page)
                outputs[writer] = output
            print("\n----------\n")
            return outputs

    # noinspection SpellCheckingInspection
    @staticmethod
    def handle_pages(notion_pages: typing.List[NotionPage]) -> typing.Dict[str, NotionDirOutput]:
        dir_outputs = {}
        for notion_page in notion_pages:
            file_outputs = NotionWriter.handle_page(notion_page)
            for channel in file_outputs.keys():
                if channel not in dir_outputs and file_outputs[channel].has_output():
                    dir_outputs[channel] = file_outputs[channel]

        return dir_outputs

    # noinspection SpellCheckingInspection
    @staticmethod
    def inspect_page(notion_page: NotionPage) -> typing.Dict[str, NotionFileOutput]:
        if not notion_page.is_markdown_able():
            print("Skip non-markdownable page: " + notion_page.get_identify())
            return {}

        if not notion_page.is_output_able():
            print("Skip non-outputable page: " + notion_page.get_identify())
            return {}

        print("Write page: " + notion_page.get_identify())
        page_writer = SpellInspectWriter()
        output = page_writer.write_page(notion_page)
        print("\n----------\n")
        return {
            "default": output
        }


class ImageDownloader:
    def need_download_image(self, block) -> bool:
        if not Config.download_image():
            return False
        if block.type != "image":
            return False
        if not str(block.image_url).startswith("http"):
            return False
        return 'keep-url-source=true' not in str(block.image_url).lower()

    def download_image(self, image_url: str, image_file):
        if FileUtils.exists(image_file):
            FileUtils.delete(image_file)
        FileUtils.create_file(image_file)
        if image_url.startswith("https://"):
            image_url = image_url.replace("https://", "http://")
        try:
            r = requests.get(image_url, allow_redirects=True, timeout=(5, 10))
            open(image_file, 'wb').write(r.content)
        except requests.exceptions.RequestException as e:
            print(e)
        pass

    def get_image_path(self, image_url, image_caption, def_ext='.jpg') -> str:
        prefix = image_url
        if '?' in image_url:
            prefix = image_url[:image_url.find('?')]
        file_name = prefix
        if '/' in prefix:
            file_name = prefix[prefix.rfind('/') + len('/'):]
            if len(file_name) <= 0 or str(file_name).lower().startswith('untitled.'):
                prefix = image_url[:image_url.rfind('/')]
                if '/' in prefix:
                    file_name = "{}-{}".format(prefix[prefix.rfind('/') + len('/'):], file_name)
                    pass

        if image_caption and len(image_caption) > 0:
            file_name = image_caption + "-" + file_name
        splitext = os.path.splitext(file_name)
        return slugify(splitext[0]) + (splitext[1] if splitext[1] else def_ext)


# noinspection PyMethodMayBeStatic
class NotionPageWriter:
    def __init__(self):
        self.root_dir = "NotionDown"
        self.assets_dir = "assets"
        self.post_dir = "post"
        self.draft_dir = "draft"
        self.block_joiner: PageBlockJoiner = PageBlockJoiner()
        self.image_downloader: ImageDownloader = ImageDownloader()

    def is_markdown_able(self, notion_page: NotionPage):
        return notion_page.get_title() is not None  # and notion_page.get_date() is not None

    def is_output_able(self, notion_page: NotionPage):
        return notion_page.get_file_name() is not None

    def write_page(self, notion_page: NotionPage) -> NotionFileOutput:
        print("#write_page")
        print("page identify = " + notion_page.get_identify())

        page_lines = self._start_writing(notion_page)
        self._on_dump_page_content(page_lines)

        file_path = self._configure_file_path(notion_page)
        self._prepare_file(file_path)
        self._write_file("\n".join(page_lines), file_path)

        properties_file_path = file_path + "_properties.json"
        self._prepare_file(properties_file_path)
        self._write_file(
            json.dumps(notion_page.properties, indent=4, ensure_ascii=False),
            properties_file_path
        )

        output = NotionFileOutput()
        output.output_dir = self._configure_root_dir()
        output.markdown_path = file_path
        output.properties_path = properties_file_path

        return output

    def _start_writing(self, notion_page: NotionPage) -> typing.List[typing.Text]:
        page_lines = []
        self._write_header(page_lines, notion_page)
        self._write_blocks(page_lines, notion_page.blocks)
        self._write_tail(page_lines, notion_page)
        return page_lines

    def _write_header(self, page_lines: typing.List[typing.Text], notion_page: NotionPage):
        page_lines.append("")
        if notion_page.cover:
            image_block = PageImageBlock()
            image_block.image_caption = "Page Cover"
            image_block.image_url = notion_page.cover
            page_lines.append(image_block.write_block())
            page_lines.append("")
        pass

    def _write_blocks(self, page_lines: typing.List[typing.Text], blocks: typing.List[PageBaseBlock] , depth=0):
        for idx in range(len(blocks)):
            self._write_block(page_lines, blocks, idx)
        pass

    def _write_block(
            self,
            page_lines: typing.List[typing.Text],
            blocks: typing.List[PageBaseBlock],
            curr_idx,
            depth=0):

        if self._on_write_block(page_lines, blocks, curr_idx):
            return

        block = blocks[curr_idx]

        # Check prefix-separator
        if self.block_joiner.should_add_separator_before(blocks, curr_idx):
            page_lines.append("")

        # Curr block
        page_lines.append(self._write_curr_block(block, depth))

        # Check suffix-separator
        if self.block_joiner.should_add_separator_after(blocks, curr_idx):
            page_lines.append("")

    def _on_write_block(
            self,
            page_lines: typing.List[typing.Text],
            blocks: typing.List[PageBaseBlock],
            curr_idx):
        block = blocks[curr_idx]
        if block.type == 'channel_block':
            if str(block.channel).lower() not in [str(it).lower() for it in Config.channels()]:
                print("Skip channel block: {}".format(block.channel))
                return True
        return False

    def _write_curr_block(self, block: PageBaseBlock, depth):
        if block.is_group():
            def handler(blocks: typing.List[PageBaseBlock])->str:
                lines = [self._write_curr_block(it, depth + 1) for it in blocks]
                return "\n".join(lines)
            block.on_write_children(handler)
            return block.write_block()

        if self.image_downloader.need_download_image(block):
            # Download image to assets dir
            image_path = self.image_downloader.get_image_path(block.image_url, block.image_caption)
            image_source = self.assets_dir + "/" + image_path
            block.image_file = FileUtils.new_file(
                self._configure_root_dir(),
                image_source
            )
            # Check if downloaded before
            if not FileUtils.exists(block.image_file):
                self.image_downloader.download_image(block.image_url, block.image_file)
            return block.write_image_block("/" + image_source)

        block_text = block.write_block()
        if block.type in ['text', 'header', 'sub_header', 'sub_sub_header', 'numbered_list', 'bulleted_list', 'quote', 'callout']:
            return self._polish_text(block_text)
        else:
            return block_text

    def _polish_text(self, text):
        if Utils.check_module_installed("pangu"):
            import pangu
            return pangu.spacing_text(text)
        else:
            return text

    def _write_tail(self, page_lines: typing.List[typing.Text], notion_page: NotionPage):
        page_lines.append("\n")
        page_lines.append("""
<!-- Generated by {}
{}
-->\n""".format(
            type(self).__name__,
            self._get_page_tail(notion_page)
        ))

    def _get_page_tail(self, notion_page: NotionPage):
        return "\n".join([
            "notion-down.version = {}".format(Config.notion_down_version()),
            "notion-down.revision = {}".format(Config.notion_down_revision()),
        ])

    def _on_dump_page_content(self, page_lines):
        pass

    def _configure_root_dir(self) -> typing.Text:
        print("#_configure_root_dir")
        root_dir = FileUtils.new_file(Config.output(), self.root_dir)
        FileUtils.create_dir(root_dir)
        return root_dir

    def _configure_file_path(self, notion_page: NotionPage) -> typing.Text:
        print("#_configure_file_path")

        base_dir = FileUtils.new_file(
            self._configure_root_dir(),
            self.post_dir if notion_page.is_published() else self.draft_dir
        )

        page_path = FileUtils.new_file(
            notion_page.get_file_dir() if notion_page.get_file_dir() else "",
            notion_page.get_file_name()
        )

        file_path = FileUtils.new_file(base_dir, page_path + ".md")
        print("file_path = " + file_path)
        return file_path

    def _prepare_file(self, file_path):
        if FileUtils.exists(file_path):
            if not Config.debuggable():
                raise Exception("file already exists: " + file_path)

        FileUtils.create_file(file_path)

    def _write_file(self, content, file_path):
        FileUtils.write_text(content, file_path)


# class GitHubWriter(NotionPageWriter):
#
#     def __init__(self):
#         super().__init__()
#         self.root_dir = "GitHub"


class ChannelWriter(NotionPageWriter):

    def __init__(self, channel):
        super().__init__()
        self.root_dir = channel
        self.channel = channel


class SpellInspectWriter(NotionPageWriter):

    def __init__(self):
        super().__init__()
        from corrects.inspect_spell import PyCorrectorInspector
        self.root_dir = "SpellInspect"
        self.inspector = PyCorrectorInspector()
        self.inspected_issues = []

    def _on_dump_page_content(self, page_lines):
        page_lines_inspected = []
        for line in page_lines:
            if line and len(str(line).strip()) > 0:
                inspect_issues = self.inspector.get_inspect_issues(line)
                if len(inspect_issues) > 0:
                    # has inspected issues
                    self.inspected_issues.append(inspect_issues)
                    formatted_text = SpellInspectWriter._format_text_with_inspect_issues(
                        line,
                        inspect_issues
                    )
                    page_lines_inspected.append(formatted_text)
                    page_lines_inspected.append('\'\'\'pycorrector')
                    page_lines_inspected.append(str(inspect_issues))
                    page_lines_inspected.append('\'\'\'')
                    continue

            page_lines_inspected.append(line)

        page_lines.clear()
        page_lines.extend(page_lines_inspected)

    def _get_page_tail(self, notion_page: NotionPage):
        return "\n".join([
            super()._get_page_tail(notion_page),
            "spell-inspector = {}".format(self.inspector.get_name()),
            "spell-inspected-issues = {}".format(len(self.inspected_issues)),
        ])

    @staticmethod
    def _format_text_with_inspect_issues(text: str, issues):
        """
        [
            ['无', '舞', 14, 15],
            ['因该', '应该', 20, 22],
            ['坐', '座', 26, 27],
            ['机七', '机器', 28, 30],
            ['领遇', '领域', 37, 39],
            ['平净', '平静', 58, 60],
            ['有明', '有名', 70, 72]
        ]
        """
        if text and len(text.strip()) > 0:
            if len(issues) > 0:
                # has inspected issues
                phases = []
                for idx, issue in enumerate(issues):
                    issue_pre = None if idx == 0 else issues[idx - 1]
                    issue_nxt = None if idx >= len(issues) - 1 else issues[idx + 1]

                    # prefix
                    if issue_pre:
                        phases.append(text[issue_pre[3]:issue[2]])
                    else:
                        phases.append(text[:issue[2]])
                    # issue_word
                    phases.append('~~{}~~'.format(text[issue[2]:issue[3]]))
                    # suffix
                    if not issue_nxt:
                        phases.append(text[issue[3]:])
                return "".join(phases)
            pass
        return text


# noinspection PyMethodMayBeStatic
class HexoWriter(NotionPageWriter):

    def __init__(self):
        super().__init__()
        self.root_dir = "Hexo"
        self.post_dir = "_posts"
        self.draft_dir = "_drafts"

    def is_output_able(self, notion_page: NotionPage):
        return super().is_output_able(notion_page) and len(notion_page.properties) > 0

    def _configure_file_path(self, notion_page: NotionPage) -> typing.Text:
        if 'hexo.page' in notion_page.properties \
                and notion_page.properties['hexo.page'] == 'true' \
                and notion_page.is_published():
            print("#_configure_file_path for hexo page")
            base_dir = self._configure_root_dir()
            page_path = FileUtils.new_file(
                notion_page.get_file_dir() if notion_page.get_file_dir() else "",
                notion_page.get_file_name()
            )
            file_path = FileUtils.new_file(base_dir, page_path + ".md")
            print("file_path = " + file_path)
            return file_path

        return super()._configure_file_path(notion_page)

    def _on_write_block(
            self,
            page_lines: typing.List[typing.Text],
            blocks: typing.List[PageBaseBlock],
            curr_idx):
        if super()._on_write_block(page_lines, blocks, curr_idx):
            return True

        block = blocks[curr_idx]
        if block.type == 'table_of_contents':
            return True
        return False

    def write_page(self, notion_page: NotionPage) -> NotionFileOutput:
        print("#write_page")
        print("page identify = " + notion_page.get_identify())

        page_lines = self._start_writing(notion_page)
        self._on_dump_page_content(page_lines)

        root_dir = self._configure_root_dir()
        file_path = self._configure_file_path(notion_page)
        self._prepare_file(file_path)
        self._write_file("\n".join(page_lines), file_path)

        output = NotionFileOutput()
        output.output_dir = root_dir
        output.markdown_path = file_path
        return output

    def _write_header(self, page_lines: typing.List[typing.Text], notion_page: NotionPage):
        # Write Hexo page front-matter according to page's properties
        front_matter_lines = self._write_front_matter(notion_page)
        if len(front_matter_lines) > 0:
            page_lines.extend(front_matter_lines)

        super()._write_header(page_lines, notion_page)

    def _write_front_matter(self, notion_page: NotionPage):
        """
        :see https://hexo.io/docs/front-matter
        """
        if len(notion_page.properties) <= 0:
            return []

        front_matter = {
            'layout': None,
            'title': None,
            'date': None,
            'updated': None,
            'comments': None,
            'tags': None,
            'categories': None,
            'permalink': None,
            'texcerptags': None,
            'disableNunjucks': None,
            'lang': None,
        }

        for key in notion_page.properties.keys():
            symbol = "hexo."
            if str(key).startswith(symbol) and len(str(key)) > len(symbol):
                hexo_key = str(key)[str(key).find(symbol) + len(symbol):]
                front_matter[hexo_key] = notion_page.properties[key]

        # NotionDown page properties to hexo front matter mapping
        #
        # [notion-down-properties]
        # Title = NotionDown Custom Page Properties Support
        # Date = 2021-05-20
        # Published = false
        # Category = NotionDown
        # Tag = Notion, NotionDown
        # FileLocate =
        # FileName =

        mapping = {
            'Title': "title",
            'Date': "date",
            'Category': "categories",
            'Tag': "tags",
        }

        for key in notion_page.properties.keys():
            if key in mapping:
                if not front_matter[mapping[key]]:
                    front_matter[mapping[key]] = notion_page.properties[key]

        # List type checking
        list_key = ['categories', 'tags']
        for key in list_key:
            if front_matter[key]:
                if type(front_matter[key]) is not list:
                    front_matter[key] = [front_matter[key]]

        if front_matter['title']:
            front_matter['title'] = self._polish_text(front_matter['title'])

        # Write front matter
        lines = ['---']
        for key in front_matter.keys():
            if not front_matter[key]:
                continue
            if type(front_matter[key]) is list:
                lines.append('{}:'.format(key))
                lines.append("\n".join([' - {}'.format(it) for it in front_matter[key]]))
            else:
                lines.append('{}: {}'.format(key, front_matter[key]))

        lines.append('---\n')
        return lines

    def _get_page_tail(self, notion_page: NotionPage):
        tail_lines = [super()._get_page_tail(notion_page)]
        for key in notion_page.properties.keys():
            tail_lines.append("{} = {}".format(key, notion_page.properties[key]))
        return "\n".join(tail_lines)

