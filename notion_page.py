import os

from notion.block import CodeBlock, ImageBlock

from config import Config


class PageBaseBlock:
    def __init__(self):
        self.type = 'base'

    def write_block(self):
        return self.type


class PageTextBlock(PageBaseBlock):
    def __init__(self):
        super().__init__()
        self.text = 'text'


class PageImageBlock(PageBaseBlock):
    def __init__(self):
        super().__init__()
        self.text = 'image'
        self.image_caption = ''
        self.image_url = ''
        self.image_file = ''


# noinspection PyBroadException
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
        self.blocks = []
        self.properties = {}

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
            return self.get_title()
        if len(self.id) > 0:
            return self.id
        return None

    def parse(self, page):
        self.id = str(page.id)
        self.title = str(page.title)

        # parse page blocks
        for block in page.children:
            if type(block) is CodeBlock:
                if '[properties]' in block.title:
                    self.parse_properties(block)
                    continue
            if type(block) is ImageBlock:
                self.parse_image(block)
                continue
            self.parse_basic(block)
        pass

    def parse_basic(self, block):
        block_type = block.type
        page_block = PageBaseBlock()
        page_block.type = block_type
        self.blocks.append(page_block)

    def parse_properties(self, block):
        content = block.title
        symbol = '[properties]'
        if symbol in content:
            content_properties = content[content.rfind(symbol) + len(symbol):]
            lines = str(content_properties).split("\n")
            for line in lines:
                if '=' in line:
                    idx = line.find('=')
                    key = line[:idx].strip()
                    value = line[idx + len('='):].strip()
                    self.properties[key] = value

    def parse_image(self, block):
        image_id = block.id
        image_caption = str(block.caption)
        image_url = str(block.source)
        temp_file = os.path.join(Config.output(), "assets/image", image_id + "_" + image_caption, ".jpg")

        page_image_block = PageImageBlock()
        page_image_block.image_caption = image_caption
        page_image_block.image_url = image_url
        page_image_block.image_file = temp_file
        self.blocks.append(page_image_block)
