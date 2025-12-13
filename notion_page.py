import os
import re
import typing
import urllib

from slugify import slugify

from notion_client import Client
from config import Config
from utils.utils import Utils
from utils.notion_utils import NotionUtils


class PageBaseBlock:
    def __init__(self):
        self.id = 'unknown'
        self.type = 'unknown'
        self.children: typing.List[PageBaseBlock] = None

    def write_block(self):
        return """<!-- unsupported page block
type: {}
{}
-->""".format(self.type, self._wip_msg())

    def _wip_msg(self):
        return "notion id: " + self.id

    def is_group(self):
        return self.children is not None


class PageGroupBlock(PageBaseBlock):
    def __init__(self):
        super().__init__()
        self.type = 'group_block'
        self.group = 'Group'
        self.name = ''
        self.children: typing.List[PageBaseBlock] = []
        self.on_write_children_handler: typing.Callable[[typing.List[PageBaseBlock]], str] = None

    def on_write_children(self, handler: typing.Callable[[typing.List[PageBaseBlock]], str]):
        self.on_write_children_handler = handler
        pass

    def write_block(self):
        if not self.on_write_children_handler:
            def handler(blocks: typing.List[PageBaseBlock])->str:
                lines = [it.write_block() for it in blocks]
                return "\n".join(lines)
            self.on_write_children_handler = handler
        text = self.on_write_children_handler(self.children)
        return "{}\n{}\n{}".format(self.write_begin(), text, self.write_end())

    def write_begin(self):
        return "<!-- {} BGN{} -->".format(self.group, '' if len(self.name) == 0 else ' ' + self.name)

    def write_end(self):
        return "<!-- {} END{} -->".format(self.group, '' if len(self.name) == 0 else ' ' + self.name)


class PageSyncedSourceBlock(PageGroupBlock):
    def __init__(self):
        super().__init__()
        self.type = 'transclusion_container'
        self.group = 'SyncedSourceBlock'
        self.children: typing.List[PageBaseBlock] = []

    def write_block(self):
        if not self.on_write_children_handler:
            def handler(blocks: typing.List[PageBaseBlock])->str:
                lines = [it.write_block() for it in blocks]
                return "\n".join(lines)
            self.on_write_children_handler = handler
        text = self.on_write_children_handler(self.children)
        return text


class PageSyncedCopyBlock(PageGroupBlock):
    def __init__(self):
        super().__init__()
        self.type = 'transclusion_reference'
        self.group = 'SyncedCopyBlock'
        self.children: typing.List[PageBaseBlock] = []

    def write_block(self):
        lines = [it.write_block() for it in self.children]
        return "<!-- SyncedBlock: {}\nThis is a reference block. {}\n-->".format(self.name, "\n".join(lines))


class PageShortCodeBlock(PageGroupBlock):
    def __init__(self):
        super().__init__()
        self.type = 'short_code_block'
        self.group = 'ShortCode'
        self.children: typing.List[PageBaseBlock] = []

    def write_block(self):
        lines = [it.write_block() for it in self.children]
        return "<!-- ShortCode: {}\n{}\n-->".format(self.name, "\n".join(lines))


class PageChannelBlock(PageGroupBlock):
    def __init__(self):
        super().__init__()
        self.type = 'channel_block'
        self.group = 'Channel'
        self.channel = ''

    def write_begin(self):
        return "<!-- For {} only BGN: {} -->".format(self.group, self.channel)

    def write_end(self):
        return "<!-- For {} only END: {} -->".format(self.group, self.channel)


class PageColumnListBlock(PageGroupBlock):
    def __init__(self):
        super().__init__()
        self.type = 'column_list'
        self.group = 'ColumnList'
        self.children: typing.List[PageColumnBlock] = []

    def write_block(self):
        if not self.on_write_children_handler:
            def handler(blocks: typing.List[PageBaseBlock])->str:
                column_lines = []
                for idx, column_block in enumerate(blocks):
                    column_lines.append(
                        "{}<!-- Column {} start -->\n{}\n<!-- Column end -->".format(
                            "\n" if idx > 0 else "",
                            idx,
                            column_block.write_block()
                        )
                    )
                return "\n".join(column_lines)
            self.on_write_children_handler = handler
        return super().write_block()


class PageColumnBlock(PageGroupBlock):
    def __init__(self):
        super().__init__()
        self.type = 'column'
        self.group = 'Column'
        self.children: typing.List[PageBaseBlock] = []
        self.block_joiner: PageBlockJoiner = PageBlockJoiner()

    def write_block(self):
        if not self.on_write_children_handler:
            def handler(blocks: typing.List[PageBaseBlock])->str:
                lines = []
                for idx in range(len(blocks)):
                    block = self.children[idx]
                    if self.block_joiner.should_add_separator_before(self.children, idx):
                        lines.append("")
                    lines.append(block.write_block())
                    if self.block_joiner.should_add_separator_after(self.children, idx):
                        lines.append("")
                return "\n".join(lines)
        text = self.on_write_children_handler(self.children)
        return text


class PageTocBlock(PageBaseBlock):
    def __init__(self):
        super().__init__()
        self.type = 'table_of_contents'
        self.page_blocks = []

    def write_block(self):
        '''
        # Table of Contents
        -. [Example](#example)
        -. [Example2](#example2)
        -.   [Third Example](#third-example)
        -.   [Fourth Example](#fourth-examplehttpwwwfourthexamplecom)
        '''

        block_lines = []
        for block in self.page_blocks:
            if block.type == "header":
                block_lines.append(" * [{}](#{})".format(block.text, str(block.text).lower().replace(" ", "-")))
            if block.type == "sub_header":
                block_lines.append(" * {}[{}](#{})".format('&nbsp;' * 4, block.text, str(block.text).lower().replace(" ", "-")))
            if block.type == "sub_sub_header":
                block_lines.append(" * {}[{}](#{})".format('&nbsp;' * 8, block.text, str(block.text).lower().replace(" ", "-")))

        return ("\n".join(block_lines)) if len(block_lines) > 0 else ""


# noinspection DuplicatedCode,PyMethodMayBeStatic
class PageTableBlock(PageBaseBlock):
    def __init__(self):
        super().__init__()
        self.type = 'collection_view'
        self.headers = [] # List of column names
        self.rows = []    # List of rows (each row is a list of cell values)

    def write_block(self):
        if not self.headers:
            return ''
        
        block_lines = []
        
        # Header
        block_lines.append("{}".format(" | ".join([str(h).replace('|', '&#124;') for h in self.headers])))
        # Separator
        block_lines.append("{}".format(" | ".join([':---:' for _ in self.headers])))
        
        # Rows
        for row in self.rows:
            # Ensure row has same length as headers
            cells = row + [''] * (len(self.headers) - len(row))
            block_lines.append("{}".format(" | ".join([str(c).replace('|', '&#124;') for c in cells[:len(self.headers)]])))

        return "\n".join(block_lines)

    def set_data(self, headers, rows):
        self.headers = headers
        self.rows = rows


class PageTextBlock(PageBaseBlock):
    def __init__(self):
        super().__init__()
        self.type = 'text'
        self.text = ''

    def write_block(self):
        # Check obfuscated links or images
        pattern = re.compile("\[.*\]\(\[.*\]\(.*\)\)")
        if pattern.search(self.text) is not None:
            # parse obfuscated blocks
            obfuscated_links = []

            try:
                p = pattern
                for m in p.finditer(self.text):
                    obfuscated_link = m.group()
                    prefix = obfuscated_link[:obfuscated_link.find("]([")] + "]"
                    link = obfuscated_link[obfuscated_link.rfind("](") + len("]("):obfuscated_link.rfind("))")]
                    obfuscated_links.append("{}({})".format(prefix, link))

                intermediate_text = re.sub(pattern, '{}', self.text)
                return intermediate_text.format(*obfuscated_links)
            except Exception as e:
                print("Parse obfuscated links block error: text = {}\t\n".format(self.text))
                raise e

        return self.text


class PageEnterBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'enter'
        self.text = ''

    def write_block(self):
        return self.text


class PageDividerBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'divider'
        self.text = '---'

    def write_block(self):
        return self.text


class PageNumberedListBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'numbered_list'
        self.text = ''
        self.level = 0

    def write_block(self):
        return '{}1. {}'.format(" " * 4 * self.level, self.text)


class PageBulletedListBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'bulleted_list'
        self.text = ''
        self.level = 0

    def write_block(self):
        return '{}- {}'.format(" " * 4 * self.level, self.text)


class PageQuoteBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'quote'
        self.text = ''

    def write_block(self):
        return '> {}'.format(self.text)


class PageCalloutBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'callout'
        self.text = ''

    def write_block(self):
        lines = str(self.text).split("\n")
        return '> ' + "> ".join(lines)


class PageHeaderBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'header'
        self.text = ''

    def write_block(self):
        return '# {}'.format(self.text)


class PageSubHeaderBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'sub_header'
        self.text = ''

    def write_block(self):
        return '## {}'.format(self.text)


class PageSubSubHeaderBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'sub_sub_header'
        self.text = ''

    def write_block(self):
        return '### {}'.format(self.text)


class PageCodeBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'code'
        self.text = ''
        self.lang = ''

    def write_block(self):
        return """```{}
{}
```
""".format(self.lang, self.text)


class PageImageBlock(PageBaseBlock):
    def __init__(self):
        super().__init__()
        self.type = 'image'
        self.image_caption = ''
        self.image_url = ''
        self.image_file = ''

    def write_block(self):
        return self.write_image_block(self.image_url)

    def write_image_block(self, image_source):
        return "![{}]({})".format(self.image_caption, image_source)


class PageToggleBlock(PageTextBlock):
    def __init__(self):
        super().__init__()
        self.type = 'image'
        self.text = ''
        self.children = []
        self.status = 'details'  # or 'details open'

    def write_block(self):
        return '''<{}>
<summary>{}</summary>
<pre><code>{}
</code></pre>
</details>'''.format(self.status, self.text, "\n".join(self.children))

    def is_group(self):
        # Flatt ToggleBlock as NonGroupBlock, because its writing is simple and no need to traversal.
        return False


# noinspection PyBroadException,PyMethodMayBeStatic
class NotionPage:
    """
    relative_path = None
    title = ''
    date = ''
    properties = {}
    blocks = []
    """

    def __init__(self):
        self.id = ''
        self.title = ''
        self.cover = ''
        self.blocks = []
        self.properties = {}

        self.mapping = {
            "paragraph": self._parse_text,
            "heading_1": self._parse_header,
            "heading_2": self._parse_sub_header,
            "heading_3": self._parse_sub_sub_header,
            "bulleted_list_item": self._parse_bulleted_list,
            "numbered_list_item": self._parse_numbered_list,
            "to_do": self._parse_to_do,
            "toggle": self._parse_toggle,
            "child_page": self._parse_sub_page,
            "child_database": self._parse_collection,
            "linked_database": self._parse_collection,
            "embed": self._parse_embed,
            "image": self._parse_image,
            "video": self._parse_video,
            "file": self._parse_file,
            "pdf": self._parse_pdf,
            "bookmark": self._parse_bookmark,
            "callout": self._parse_callout,
            "quote": self._parse_quote,
            "equation": self._parse_equation,
            "divider": self._parse_divider,
            "table_of_contents": self._parse_toc,
            "column_list": self._parse_column_list,
            "column": self._parse_column,
            "code": self._parse_code,
            "synced_block": self._parse_synced_block,
        }

    def is_markdown_able(self):
        return self.get_title() is not None  # and self.get_date() is not None

    def is_output_able(self):
        return self.get_file_name() is not None

    def get_identify(self):
        return "[{}]{}".format(self.id, self.get_title())

    def get_title(self):
        if 'Title' in self.properties:
            try:
                value = str(self.properties['Title'])
                if len(value) > 0:
                    return value
            except Exception as e:
                print(e)

        if len(self.title) > 0:
            return self.title
        return None

    def get_date(self):
        if 'Date' in self.properties:
            try:
                value = str(self.properties['Date'])
                if len(value) > 0:
                    return value
            except Exception as e:
                print(e)
        return None

    def get_category(self):
        if 'Category' in self.properties:
            try:
                return str(self.properties['Category'])
            except Exception as e:
                print(e)
        return None

    def get_tag(self):
        if 'Tag' in self.properties:
            try:
                return str(self.properties['Tag'])
            except Exception as e:
                print(e)
        return None

    def is_published(self):
        if 'Published' in self.properties:
            try:
                return str(self.properties['Published']) in [
                    'true',
                    '1',
                    't',
                    'y',
                    'yes',
                    'yeah',
                    'yup',
                    'certainly',
                    'uh-huh'
                ]
            except Exception as e:
                print(e)
        return False

    def get_file_dir(self):
        if 'FileLocate' in self.properties:
            try:
                value = str(self.properties['FileLocate'])
                if len(value) > 0:
                    return value
            except Exception as e:
                print(e)
        return None

    def get_file_name(self):
        if 'FileName' in self.properties:
            try:
                value = str(self.properties['FileName'])
                if len(value) > 0:
                    return value
            except Exception as e:
                print(e)

        if len(self.get_title()) > 0:
            return slugify(self.get_title(), separator='_')
        if len(self.id) > 0:
            return self.id
        return None

    def parse(self, page):
        self.id = page.get('id')
        # Title extraction depends on whether it's a page or a block, but usually page
        self.title = self._get_title(page)
        
        cover = page.get('cover')
        if cover:
            if cover.get('type') == 'external':
                self.cover = cover.get('external', {}).get('url')
            elif cover.get('type') == 'file':
                self.cover = cover.get('file', {}).get('url')

        # parse page blocks
        # We need to fetch children blocks
        children = self._get_children(self.id)
        self.blocks = self._parse_page_blocks(children)
        
        # Parse properties (for Hexo front-matter)
        # In official API, properties are in page['properties']
        # But we also support [notion-down-properties] in code blocks.
        # We should check for that during block parsing.
        self._parse_page_properties(page)

    def _get_title(self, page):
        properties = page.get('properties', {})
        for key, value in properties.items():
            if value.get('type') == 'title':
                return NotionUtils.get_plain_text(value.get('title', []))
        return "Untitled"

    def _get_children(self, block_id):
        # TODO: Reuse client from NotionReader or create new?
        # Creating new for now to avoid circular import issues
        client = Client(auth=Config.notion_token())
        children = []
        has_more = True
        start_cursor = None
        while has_more:
            response = client.blocks.children.list(block_id=block_id, start_cursor=start_cursor)
            children.extend(response.get('results', []))
            has_more = response.get('has_more')
            start_cursor = response.get('next_cursor')
        return children

    def _parse_page_properties(self, page):
        # Parse native Notion properties
        properties = page.get('properties', {})
        for key, value in properties.items():
            # Map Notion properties to self.properties
            # This is different from [notion-down-properties] which are custom overrides
            # But we might want to use them as defaults?
            # For now, let's just store them if needed, but the original code 
            # relied on [notion-down-properties] block or page properties.
            # The original code:
            # if 'Title' in self.properties: ...
            # Let's try to extract some common ones.
            if value.get('type') == 'date':
                date = value.get('date')
                if date:
                    self.properties['Date'] = date.get('start')
            elif value.get('type') == 'multi_select':
                options = value.get('multi_select', [])
                self.properties['Tag'] = [opt.get('name') for opt in options]
            elif value.get('type') == 'select':
                opt = value.get('select')
                if opt:
                    self.properties['Category'] = opt.get('name')
            elif value.get('type') == 'checkbox':
                self.properties['Published'] = str(value.get('checkbox')).lower()
        
        pass

    def _parse_page_blocks(self, blocks):
        page_blocks: typing.List[PageBaseBlock] = []

        # parse page blocks
        idx = 0
        while idx < len(blocks):
            block = blocks[idx]

            # Channel Block START
            if self._is_short_code_start(block):
                idx_end = self._parse_short_code_chunks(page_blocks, blocks, idx)
                if idx_end > idx:
                    idx = idx_end
                    continue

            # Basic Parsing
            self._parse_page_blocks_flatt(page_blocks, block)
            idx += 1

        return page_blocks

    def _parse_page_blocks_flatt(self, page_blocks: typing.List[PageBaseBlock], block):
        '''
        Only parse non-group block here.
        '''
        block_type = block.get('type')
        # Mapping for parse
        if block_type in self.mapping:
            self.mapping[block_type].__call__(page_blocks, block)
        else:
            # Basic Block Parsing
            self._parse_basic(page_blocks, block)

        return page_blocks

    def _is_short_code_start(self, block):
        if block.get('type') == "paragraph":
            text = NotionUtils.get_plain_text(block.get('paragraph', {}).get('rich_text', []))
            if str(text).startswith("<!-- SHORT_CODE_"):
                return True
        return False

    def _is_short_code_end(self, block):
        if block.get('type') == "paragraph":
            text = NotionUtils.get_plain_text(block.get('paragraph', {}).get('rich_text', []))
            if str(text).startswith("SHORT_CODE_END -->"):
                return True
        return False

    def _parse_short_code_chunks(self, page_blocks: typing.List[PageBaseBlock], blocks, idx_start):
        if idx_start < 0 or idx_start >= len(blocks) - 1:
            return -1

        if not self._is_short_code_start(blocks[idx_start]):
            return -1

        start_line = NotionUtils.get_plain_text(blocks[idx_start].get('paragraph', {}).get('rich_text', []))
        block_id = blocks[idx_start].get('id')

        group_block: PageGroupBlock = PageGroupBlock()
        group_block.id = block_id

        symbol = 'SHORT_CODE_'
        if symbol in start_line:
            group_block = PageShortCodeBlock()
            group_block.id = block_id
            name = start_line[start_line.rfind(symbol) + len(symbol):].strip()
            symbol_end = "="
            if symbol_end in name:
                name = name[:name.find(symbol_end)]
            group_block.name = name
            pass

        symbol = 'SHORT_CODE_CHANNEL='
        if symbol in start_line:
            group_block = PageChannelBlock()
            group_block.id = block_id
            group_block.name = 'CHANNEL'
            channel = start_line[start_line.rfind(symbol) + len(symbol):].strip()
            group_block.channel = channel
            pass

        channel_blocks: typing.List[PageBaseBlock] = []

        end_found = False
        idx = idx_start + 1
        while idx < len(blocks):
            block = blocks[idx]

            # Channel Block END
            if self._is_short_code_end(block):
                end_found = True
                break

            # Mapping for parse
            block_type = block.get('type')
            if block_type in self.mapping:
                self.mapping[block_type].__call__(channel_blocks, block)
                idx += 1
                continue

            # Basic Block Parsing
            idx += 1
            self._parse_basic(channel_blocks, block)

        if end_found:
            group_block.children = channel_blocks
            page_blocks.append(group_block)
            return idx + 1

        return -1

    def _parse_basic(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageBaseBlock()
        page_block.id = block.get('id')
        page_block.type = block.get('type')
        page_blocks.append(page_block)

    def _parse_text(self, page_blocks: typing.List[PageBaseBlock], block):
        text = NotionUtils.get_markdown_text(block.get('paragraph', {}).get('rich_text', []))
        if len(str(text).strip()) == 0:
            page_blocks.append(PageEnterBlock())
            return
        page_block = PageTextBlock()
        page_block.id = block.get('id')
        page_block.type = 'text' # internal type
        page_block.text = text
        page_blocks.append(page_block)
        pass

    def _parse_image(self, page_blocks: typing.List[PageBaseBlock], block):
        image_id = block.get('id')
        image_info = block.get('image', {})
        # Caption
        image_caption = NotionUtils.get_plain_text(image_info.get('caption', []))
        
        # URL
        image_url = ""
        if image_info.get('type') == 'external':
            image_url = image_info.get('external', {}).get('url')
        elif image_info.get('type') == 'file':
            image_url = image_info.get('file', {}).get('url')

        temp_file = os.path.join(Config.output(), "assets/image", image_id + "_" + image_caption, ".jpg")

        page_block = PageImageBlock()
        page_block.id = image_id
        page_block.type = 'image'
        page_block.image_caption = image_caption
        page_block.image_url = image_url
        page_block.image_file = temp_file
        page_blocks.append(page_block)

    def _parse_divider(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageDividerBlock()
        page_block.id = block.get('id')
        page_block.type = 'divider'
        page_blocks.append(page_block)

    def _parse_properties(self, block):
        # Properties in code block [notion-down-properties]
        content = NotionUtils.get_plain_text(block.get('code', {}).get('rich_text', []))
        symbol = '[notion-down-properties]'
        if symbol in content:
            content_properties = content[content.rfind(symbol) + len(symbol):]
            lines = str(content_properties).split("\n")
            for line in lines:
                if '=' in line:
                    idx = line.find('=')
                    key = line[:idx].strip()
                    value = line[idx + len('='):].strip()
                    if ',' in value:
                        # list
                        self.properties[key] = [it.strip() for it in value.split(',')]
                        continue
                    self.properties[key] = value

    def _parse_code(self, page_blocks: typing.List[PageBaseBlock], block):
        content = NotionUtils.get_plain_text(block.get('code', {}).get('rich_text', []))
        symbol = '[notion-down-properties]'
        if symbol in content:
            self._parse_properties(block)
            return

        page_block = PageCodeBlock()
        page_block.id = block.get('id')
        page_block.type = 'code'
        page_block.text = content
        page_block.lang = block.get('code', {}).get('language', 'plain text')
        page_blocks.append(page_block)

    def _parse_numbered_list(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageNumberedListBlock()
        page_block.id = block.get('id')
        page_block.type = 'numbered_list'
        page_block.text = NotionUtils.get_markdown_text(block.get('numbered_list_item', {}).get('rich_text', []))
        page_block.level = 0
        page_blocks.append(page_block)

        if block.get('has_children'):
            children = self._get_children(block.get('id'))
            self.__recursive_parse_numbered_list(page_blocks, children, page_block.level + 1)
            pass

    def __recursive_parse_numbered_list(self, page_blocks: typing.List[PageBaseBlock], blocks, level):
        for block in blocks:
            page_block = PageNumberedListBlock()
            page_block.id = block.get('id')
            page_block.type = 'numbered_list'
            # Check if it's actually a numbered list item, otherwise treat as text or whatever
            # But usually nested list items are same type.
            if block.get('type') == 'numbered_list_item':
                page_block.text = NotionUtils.get_markdown_text(block.get('numbered_list_item', {}).get('rich_text', []))
            else:
                # Handle mixed content in list? For now just try to extract text if possible or ignore
                # Or maybe we should parse it properly?
                # The original code assumed children are list items.
                # Let's try to get text if it's a paragraph or list item.
                type_ = block.get('type')
                if type_ in ['paragraph', 'bulleted_list_item', 'numbered_list_item']:
                     page_block.text = NotionUtils.get_markdown_text(block.get(type_, {}).get('rich_text', []))
                else:
                     page_block.text = f"[{type_}]"

            page_block.level = level
            page_blocks.append(page_block)

            if block.get('has_children'):
                children = self._get_children(block.get('id'))
                self.__recursive_parse_numbered_list(page_blocks, children, level + 1)
                pass

    def _parse_bulleted_list(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageBulletedListBlock()
        page_block.id = block.get('id')
        page_block.type = 'bulleted_list'
        page_block.text = NotionUtils.get_markdown_text(block.get('bulleted_list_item', {}).get('rich_text', []))
        page_block.level = 0
        page_blocks.append(page_block)

        if block.get('has_children'):
            children = self._get_children(block.get('id'))
            self.__recursive_parse_bulleted_list(page_blocks, children, page_block.level + 1)
            pass

    def __recursive_parse_bulleted_list(self, page_blocks: typing.List[PageBaseBlock], blocks, level):
        for block in blocks:
            page_block = PageBulletedListBlock()
            page_block.id = block.get('id')
            page_block.type = 'bulleted_list'
            
            type_ = block.get('type')
            if type_ == 'bulleted_list_item':
                page_block.text = NotionUtils.get_markdown_text(block.get('bulleted_list_item', {}).get('rich_text', []))
            elif type_ in ['paragraph', 'numbered_list_item']:
                 page_block.text = NotionUtils.get_markdown_text(block.get(type_, {}).get('rich_text', []))
            else:
                 page_block.text = f"[{type_}]"

            page_block.level = level
            page_blocks.append(page_block)

            if block.get('has_children'):
                children = self._get_children(block.get('id'))
                self.__recursive_parse_bulleted_list(page_blocks, children, level + 1)
                pass

    def _parse_quote(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageQuoteBlock()
        page_block.id = block.get('id')
        page_block.type = 'quote'
        page_block.text = NotionUtils.get_markdown_text(block.get('quote', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_callout(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageCalloutBlock()
        page_block.id = block.get('id')
        page_block.type = 'callout'
        page_block.text = NotionUtils.get_markdown_text(block.get('callout', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_header(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageHeaderBlock()
        page_block.id = block.get('id')
        page_block.type = 'header'
        page_block.text = NotionUtils.get_markdown_text(block.get('heading_1', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_sub_header(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageSubHeaderBlock()
        page_block.id = block.get('id')
        page_block.type = 'sub_header'
        page_block.text = NotionUtils.get_markdown_text(block.get('heading_2', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_sub_sub_header(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageSubSubHeaderBlock()
        page_block.id = block.get('id')
        page_block.type = 'sub_sub_header'
        page_block.text = NotionUtils.get_markdown_text(block.get('heading_3', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_to_do(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageBaseBlock() # Use generic for now or create PageToDoBlock
        # We can reuse PageBulletedListBlock or similar if we don't have a specific class
        # Or just treat as text with checkbox.
        # Let's create a simple text representation for now: "[ ] Task" or "[x] Task"
        checked = block.get('to_do', {}).get('checked', False)
        text = NotionUtils.get_markdown_text(block.get('to_do', {}).get('rich_text', []))
        prefix = "[x] " if checked else "[ ] "
        
        page_block.id = block.get('id')
        page_block.type = 'to_do' # internal type
        # We don't have PageToDoBlock, so let's use PageTextBlock but with modified text?
        # Or just append to page_blocks as a text block.
        # Actually, let's use PageBulletedListBlock but change type to 'to_do' if we want specific rendering,
        # but for Markdown, it's `- [ ]`.
        # Let's use PageTextBlock and format it manually for now.
        page_block = PageTextBlock()
        page_block.id = block.get('id')
        page_block.type = 'to_do'
        page_block.text = prefix + text
        page_blocks.append(page_block)

    def _parse_embed(self, page_blocks: typing.List[PageBaseBlock], block):
        # Generic embed
        url = block.get('embed', {}).get('url', '')
        page_block = PageTextBlock()
        page_block.id = block.get('id')
        page_block.type = 'embed'
        page_block.text = f"<{url}>"
        page_blocks.append(page_block)

    def _parse_video(self, page_blocks: typing.List[PageBaseBlock], block):
        # Video
        video = block.get('video', {})
        url = ""
        if video.get('type') == 'external':
            url = video.get('external', {}).get('url')
        elif video.get('type') == 'file':
            url = video.get('file', {}).get('url')
        
        page_block = PageTextBlock()
        page_block.id = block.get('id')
        page_block.type = 'video'
        page_block.text = f"Video: <{url}>"
        page_blocks.append(page_block)

    def _parse_file(self, page_blocks: typing.List[PageBaseBlock], block):
        file_info = block.get('file', {})
        url = ""
        if file_info.get('type') == 'external':
            url = file_info.get('external', {}).get('url')
        elif file_info.get('type') == 'file':
            url = file_info.get('file', {}).get('url')
        
        caption = NotionUtils.get_markdown_text(file_info.get('caption', []))
        text = caption if caption else "File"
        
        page_block = PageTextBlock()
        page_block.id = block.get('id')
        page_block.type = 'file'
        page_block.text = f"[{text}]({url})"
        page_blocks.append(page_block)

    def _parse_pdf(self, page_blocks: typing.List[PageBaseBlock], block):
        self._parse_file(page_blocks, block)

    def _parse_bookmark(self, page_blocks: typing.List[PageBaseBlock], block):
        url = block.get('bookmark', {}).get('url', '')
        page_block = PageTextBlock()
        page_block.id = block.get('id')
        page_block.type = 'bookmark'
        page_block.text = f"<{url}>"
        page_blocks.append(page_block)

    def _parse_equation(self, page_blocks: typing.List[PageBaseBlock], block):
        expression = block.get('equation', {}).get('expression', '')
        page_block = PageTextBlock()
        page_block.id = block.get('id')
        page_block.type = 'equation'
        page_block.text = f"$$ {expression} $$"
        page_blocks.append(page_block)

    def _parse_toc(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageTocBlock()
        page_block.id = block.get('id')
        page_block.type = 'table_of_contents'
        page_block.page_blocks = page_blocks
        page_blocks.append(page_block)

    # noinspection PyUnusedLocal
    def _parse_sub_page(self, page_blocks: typing.List[PageBaseBlock], block):
        print("Ignore subpage block within page")
        # In official API, child_page is a block.
        # We might want to link to it?
        pass

    def _parse_column_weights(self, description_rich_text):
        """Parse column weight configuration from database description.
        
        This is a wrapper around DatabaseColumnOrderingUtils.parse_column_weights
        that handles the rich text to plain text conversion.
        """
        if not description_rich_text:
            return None
        
        from utils.notion_utils import NotionUtils
        from utils.database_utils import DatabaseColumnOrderingUtils
        
        text = NotionUtils.get_plain_text(description_rich_text)
        return DatabaseColumnOrderingUtils.parse_column_weights(text)
    
    def _sort_columns_by_weight(self, headers, weights):
        """Sort columns based on weight configuration.
        
        This is a wrapper around DatabaseColumnOrderingUtils.sort_columns_by_weight.
        """
        from utils.database_utils import DatabaseColumnOrderingUtils
        return DatabaseColumnOrderingUtils.sort_columns_by_weight(headers, weights)

    def _parse_collection(self, page_blocks: typing.List[PageBaseBlock], block):
        db_id = None
        if block.get('type') == 'child_database':
            db_id = block.get('id')
        elif block.get('type') == 'linked_database':
            db_id = block.get('linked_database', {}).get('database_id')
        
        if not db_id:
            return

        try:
            client = Client(auth=Config.notion_token())
            # Check for SSL Ignore flag
            ignore_ssl = os.environ.get('NOTION_IGNORE_SSL', 'false').lower() == 'true'
            if ignore_ssl:
                import httpx
            
            from notion_reader import NotionReader
            client = NotionReader.get_client()
            
            # Retrieve database schema and description
            database = client.databases.retrieve(database_id=db_id)
            properties = database.get('properties', {})
            
            # Parse column weight configuration from description
            description = database.get('description', [])
            column_weights = self._parse_column_weights(description)
            
            # Prepare HTTP client
            http_client_req = None
            should_close_client = False
            
            if ignore_ssl:
                # Priority: if SSL ignore is requested, use our own client
                http_client_req = httpx.Client(verify=False)
                should_close_client = True
            elif hasattr(client, 'client') and client.client:
                http_client_req = client.client
            else:
                http_client_req = httpx.Client()
                should_close_client = True

            token = Config.notion_token()
            headers_http = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            url = f"https://api.notion.com/v1/databases/{db_id}/query"

            # Determine sorting logic using utility class
            from utils.database_utils import DatabaseColumnOrderingUtils
            sorts = DatabaseColumnOrderingUtils.get_database_sorts(properties)
        
            # If properties are empty (common with Inline Databases), we miss schema info for sorting.
            # Perform a pre-query to infer schema from the first row to check for 'Order' column.
            is_default_sort = len(sorts) == 1 and sorts[0].get('timestamp') == 'created_time'
            
            if not properties and is_default_sort:
                # Pre-query one row to check schema
                pre_query_body = {
                    "page_size": 1,
                    "sorts": sorts # Default sort
                }
                try:
                    pre_response = http_client_req.post(url, headers=headers_http, json=pre_query_body)
                    pre_response.raise_for_status()
                    pre_results = pre_response.json().get('results', [])
                    
                    if pre_results:
                        # Infer properties from row data
                        inferred_props = pre_results[0].get('properties', {})
                        sorts = DatabaseColumnOrderingUtils.get_database_sorts(inferred_props)
                except Exception as e:
                    print(f"Failed to infer schema for sorting: {e}")

            query_body = {
                "sorts": sorts
            }
            
            response = http_client_req.post(url, headers=headers_http, json=query_body)
            
            response.raise_for_status()
            results = response.json().get('results', [])
            
            headers = list(properties.keys()) if properties else []
            if not headers and results:
                # Infer headers from the first row if schema properties are empty
                first_row_props = results[0].get('properties', {})
                headers = list(first_row_props.keys())
            
            # Apply column ordering
            if headers and column_weights:
                headers = self._sort_columns_by_weight(headers, column_weights)
            
            rows = []
            for page in results:
                row_data = []
                page_props = page.get('properties', {})
                for header in headers:
                    if header in page_props:
                        row_data.append(self._parse_property_value(page_props[header]))
                    else:
                        row_data.append("")
                rows.append(row_data)
            
            page_block = PageTableBlock()
            page_block.id = block.get('id')
            page_block.set_data(headers, rows)
            page_blocks.append(page_block)

        except Exception as e:
            print(f"Failed to parse database {db_id}: {e}")
            page_block = PageBaseBlock()
            page_block.id = block.get('id')
            page_block.type = 'collection_view_error'
            page_block.text = f"Error parsing database: {e}"
            page_blocks.append(page_block)
        finally:
            if should_close_client and http_client_req:
                http_client_req.close()

    def _parse_property_value(self, prop_value):
        """Parse various property types to string"""
        prop_type = prop_value.get('type')
        
        if prop_type == 'title':
            return NotionUtils.get_markdown_text(prop_value.get('title', []))
        
        elif prop_type == 'rich_text':
            return NotionUtils.get_markdown_text(prop_value.get('rich_text', []))
        
        elif prop_type == 'number':
            return str(prop_value.get('number', ''))
        
        elif prop_type == 'select':
            return prop_value.get('select', {}).get('name', '') if prop_value.get('select') else ''
        
        elif prop_type == 'multi_select':
            return ', '.join([item.get('name', '') for item in prop_value.get('multi_select', [])])
        
        elif prop_type == 'date':
            date = prop_value.get('date')
            if date:
                start = date.get('start')
                end = date.get('end')
                return f"{start} -> {end}" if end else start
            return ''
        
        elif prop_type == 'checkbox':
            return 'Yes' if prop_value.get('checkbox') else 'No'
        
        elif prop_type == 'url':
            return prop_value.get('url', '') or ''
        
        elif prop_type == 'email':
            return prop_value.get('email', '') or ''
        
        elif prop_type == 'phone_number':
            return prop_value.get('phone_number', '') or ''
        
        elif prop_type == 'status':
            return prop_value.get('status', {}).get('name', '') if prop_value.get('status') else ''
        
        elif prop_type == 'people':
            return ', '.join([person.get('name', '') for person in prop_value.get('people', [])])
        
        elif prop_type == 'files':
            return ', '.join([file.get('name', '') for file in prop_value.get('files', [])])
        
        elif prop_type == 'relation':
            return f"{len(prop_value.get('relation', []))} related"
            
        elif prop_type == 'formula':
            formula = prop_value.get('formula', {})
            f_type = formula.get('type')
            if f_type == 'string':
                return formula.get('string', '')
            elif f_type == 'number':
                return str(formula.get('number', ''))
            elif f_type == 'boolean':
                return 'Yes' if formula.get('boolean') else 'No'
            elif f_type == 'date':
                date = formula.get('date')
                if date:
                    return date.get('start', '')
                return ''
                
        elif prop_type == 'created_time':
            return prop_value.get('created_time', '')
            
        elif prop_type == 'last_edited_time':
            return prop_value.get('last_edited_time', '')
            
        return ''

    def _parse_toggle(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageToggleBlock()
        page_block.id = block.get('id')
        page_block.type = 'toggle'
        page_block.text = NotionUtils.get_markdown_text(block.get('toggle', {}).get('rich_text', []))
        
        if block.get('has_children'):
            children = self._get_children(block.get('id'))
            # We need to parse children and add their text/content to page_block.children
            # But PageToggleBlock.children expects strings (lines)? 
            # Original code: for child in block.children: page_block.children.append(child.title)
            # This seems to assume children are text blocks.
            # Let's try to parse them properly.
            # But PageToggleBlock implementation writes: <pre><code>...</code></pre>
            # It seems it expects code or text.
            # Let's just extract text from children.
            for child in children:
                # Try to get text from common blocks
                type_ = child.get('type')
                text = ""
                if type_ == 'paragraph':
                    text = NotionUtils.get_plain_text(child.get('paragraph', {}).get('rich_text', []))
                elif type_ == 'code':
                     text = NotionUtils.get_plain_text(child.get('code', {}).get('rich_text', []))
                
                if text:
                    page_block.children.append(text)

        page_blocks.append(page_block)

    def _parse_column_list(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageColumnListBlock()
        page_block.id = block.get('id')
        page_block.type = 'column_list'

        page_column_blocks: typing.List[PageColumnBlock] = []
        page_block.children = page_column_blocks

        if block.get('has_children'):
            children = self._get_children(block.get('id'))
            for child in children:
                if child.get('type') == 'column':
                    self._parse_column(page_column_blocks, child)

        page_blocks.append(page_block)

    def _parse_column(self, page_blocks: typing.List[PageColumnBlock], block):
        page_block = PageColumnBlock()
        page_block.id = block.get('id')
        page_block.type = 'column'

        column_blocks: typing.List[PageBaseBlock] = []
        page_block.children = column_blocks

        if block.get('has_children'):
            children = self._get_children(block.get('id'))
            for child in children:
                self._parse_page_blocks_flatt(column_blocks, child)

        page_blocks.append(page_block)

    def _parse_synced_block(self, page_blocks: typing.List[PageBaseBlock], block):
        # synced_block can be source or reference.
        # If synced_from is None, it's source.
        synced_from = block.get('synced_block', {}).get('synced_from')
        
        if synced_from is None:
            # Source
            page_block = PageSyncedSourceBlock()
            page_block.id = block.get('id')
            page_block.type = 'transclusion_container' # Keep internal type
            
            column_blocks: typing.List[PageBaseBlock] = []
            page_block.children = column_blocks
            
            if block.get('has_children'):
                children = self._get_children(block.get('id'))
                for child in children:
                    self._parse_page_blocks_flatt(column_blocks, child)
            
            page_blocks.append(page_block)
        else:
            # Reference (Copy)
            page_block = PageSyncedCopyBlock()
            page_block.id = block.get('id')
            page_block.type = 'transclusion_reference' # Keep internal type
            
            # For reference, we might need to fetch the original block?
            # Or does the API return children for reference too?
            # API says: "The synced_block request will return the block content... 
            # If it's a duplicate, it will have a synced_from property... 
            # To get the content, you need to retrieve the original block's children."
            # But `has_children` might be true?
            # Actually, for synced block copy, we usually want to render the content.
            # If `has_children` is true, we can just fetch them.
            
            column_blocks: typing.List[PageBaseBlock] = []
            page_block.children = column_blocks
            
            if block.get('has_children'):
                children = self._get_children(block.get('id'))
                for child in children:
                    self._parse_page_blocks_flatt(column_blocks, child)
            elif synced_from:
                 # Fetch from source
                 source_id = synced_from.get('block_id')
                 children = self._get_children(source_id)
                 for child in children:
                    self._parse_page_blocks_flatt(column_blocks, child)

            page_blocks.append(page_block)

    def _parse_synced_source(self, page_blocks: typing.List[PageColumnBlock], block):
        # Deprecated, mapped to _parse_synced_block
        pass

    def _parse_synced_copy(self, page_blocks: typing.List[PageColumnBlock], block):
        # Deprecated, mapped to _parse_synced_block
        pass

    def _parse_stub(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageBaseBlock()
        page_block.id = block.id
        page_block.type = block.type
        page_blocks.append(page_block)
        raise Exception('Stub!')


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class PageBlockJoiner:
    def should_add_separator_before(
            self,
            blocks: typing.List[PageBaseBlock],
            curr_idx) -> bool:

        block = blocks[curr_idx]
        block_pre = None if curr_idx <= 0 else blocks[curr_idx - 1]
        block_nxt = None if curr_idx >= len(blocks) - 1 else blocks[curr_idx + 1]
        result = False

        # Check prefix-separator
        if block.type in ['enter']:
            pass
        else:
            if not block_pre:
                pass
            else:
                if block_pre.type in ['enter']:
                    pass
                else:
                    if block_pre.type in ['bulleted_list', 'numbered_list']:
                        if block.type in ['bulleted_list', 'numbered_list']:
                            pass
                        else:
                            result = True
                    elif block_pre.type in ['text'] and block.type in ['text']:
                        pass
                    else:
                        result = True

        return result

    def should_add_separator_after(
            self,
            blocks: typing.List[PageBaseBlock],
            curr_idx) -> bool:

        block = blocks[curr_idx]
        block_pre = None if curr_idx <= 0 else blocks[curr_idx - 1]
        block_nxt = None if curr_idx >= len(blocks) - 1 else blocks[curr_idx + 1]
        result = False

        # Check suffix-separator
        if block_nxt is None:
            result = True

        return result
