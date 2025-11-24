import os
import re
import typing
import urllib

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
        self.block = None

    def write_block(self):
        if not self.block:
            return ''
        block_lines = []

        column_properties = self.block.collection.get_schema_properties()
        ordered_column_ids = self.block.views[0].get("format.table_properties")

        ordered_column_properties = []
        for id in ordered_column_ids:
            ordered_column_properties.append(Utils.find_one(
                column_properties,
                lambda it: it['id'] == id['property']
            ))

        slugs = [it['slug'] for it in ordered_column_properties]
        types = [it['type'] for it in ordered_column_properties]

        block_lines.append("{}".format(" | ".join([str(it['name']).replace('|', '&#124;') for it in ordered_column_properties])))
        block_lines.append("{}".format(" | ".join([':---:' for it in ordered_column_properties])))

        for row in self.block.collection.get_rows():
            contents = []
            for idx, slug in enumerate(slugs):
                item_type = types[idx]
                item_value = getattr(row, slug)
                contents.append(str(self.__parse_collection_item(item_type, item_value)).replace('|', '&#124;'))
            block_lines.append("{}".format(" | ".join(contents)))

        return "\n".join(block_lines)

    def __parse_collection_item(self, collection_type, item):
        if item is None:
            return str(item)

        if collection_type == "date":
            if item.end:
                return "{} - {}".format(item.start, item.end)
            return "{}".format(item.start)

        if collection_type == 'person':
            users = []
            for user in item:
                if user.email:
                    users.append("{} <{}>".format(user.full_name, user.email))
                else:
                    users.append("{}".format(user.full_name))
            return ", ".join(users)

        if collection_type == "file":
            urls = []
            for url in item:
                file_name = None
                if '/' in url:
                    file_name = url[url.rfind('/') + len('/'):]
                    if '?' in file_name:
                        file_name = file_name[:file_name.find('?')]
                if file_name:
                    urls.append("[{}]({})".format(file_name, url))
                else:
                    urls.append(url)
            return ", ".join(urls)

        return str(item)


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
        return '{} - {}'.format(" " * 4 * self.level, self.text)


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
            return slugify(self.get_title())
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
        text = NotionUtils.get_plain_text(block.get('paragraph', {}).get('rich_text', []))
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
        page_block.text = NotionUtils.get_plain_text(block.get('numbered_list_item', {}).get('rich_text', []))
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
                page_block.text = NotionUtils.get_plain_text(block.get('numbered_list_item', {}).get('rich_text', []))
            else:
                # Handle mixed content in list? For now just try to extract text if possible or ignore
                # Or maybe we should parse it properly?
                # The original code assumed children are list items.
                # Let's try to get text if it's a paragraph or list item.
                type_ = block.get('type')
                if type_ in ['paragraph', 'bulleted_list_item', 'numbered_list_item']:
                     page_block.text = NotionUtils.get_plain_text(block.get(type_, {}).get('rich_text', []))
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
        page_block.text = NotionUtils.get_plain_text(block.get('bulleted_list_item', {}).get('rich_text', []))
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
                page_block.text = NotionUtils.get_plain_text(block.get('bulleted_list_item', {}).get('rich_text', []))
            elif type_ in ['paragraph', 'numbered_list_item']:
                 page_block.text = NotionUtils.get_plain_text(block.get(type_, {}).get('rich_text', []))
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
        page_block.text = NotionUtils.get_plain_text(block.get('quote', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_callout(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageCalloutBlock()
        page_block.id = block.get('id')
        page_block.type = 'callout'
        page_block.text = NotionUtils.get_plain_text(block.get('callout', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_header(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageHeaderBlock()
        page_block.id = block.get('id')
        page_block.type = 'header'
        page_block.text = NotionUtils.get_plain_text(block.get('heading_1', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_sub_header(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageSubHeaderBlock()
        page_block.id = block.get('id')
        page_block.type = 'sub_header'
        page_block.text = NotionUtils.get_plain_text(block.get('heading_2', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_sub_sub_header(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageSubSubHeaderBlock()
        page_block.id = block.get('id')
        page_block.type = 'sub_sub_header'
        page_block.text = NotionUtils.get_plain_text(block.get('heading_3', {}).get('rich_text', []))
        page_blocks.append(page_block)

    def _parse_to_do(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageBaseBlock() # Use generic for now or create PageToDoBlock
        # We can reuse PageBulletedListBlock or similar if we don't have a specific class
        # Or just treat as text with checkbox.
        # Let's create a simple text representation for now: "[ ] Task" or "[x] Task"
        checked = block.get('to_do', {}).get('checked', False)
        text = NotionUtils.get_plain_text(block.get('to_do', {}).get('rich_text', []))
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
        
        caption = NotionUtils.get_plain_text(file_info.get('caption', []))
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

    def _parse_collection(self, page_blocks: typing.List[PageBaseBlock], block):
        # TODO: Implement database parsing using official API
        # block.type is 'child_database'
        # We need to query the database to get rows.
        print(f"Database block {block.get('id')} not fully supported yet.")
        page_block = PageBaseBlock()
        page_block.id = block.get('id')
        page_block.type = 'collection_view' # Keep type for now or change?
        # We can't easily render it without querying.
        # Let's just append a placeholder or nothing.
        # page_blocks.append(page_block)
        pass

    def _parse_toggle(self, page_blocks: typing.List[PageBaseBlock], block):
        page_block = PageToggleBlock()
        page_block.id = block.get('id')
        page_block.type = 'toggle'
        page_block.text = NotionUtils.get_plain_text(block.get('toggle', {}).get('rich_text', []))
        
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
