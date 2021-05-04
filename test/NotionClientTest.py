import os
import unittest

from urllib.request import quote
from notion.block import CodeBlock, ImageBlock
from notion.client import NotionClient
from notion.settings import BASE_URL

from utils.utils import Utils


class NotionClientTest(unittest.TestCase):

    def test_check_token(self):
        self.assertTrue("NOTION_TOKEN_V2" in os.environ, "Token exist")

    def test_test_get_page(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))
        pass


class NotionClientMarkDownPageTest(unittest.TestCase):

    def test_test_get_md_page(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_page = Utils.find_one(page.children, lambda it: it and str(it.title) == "MarkDown Test Page")
        self.assertIsNotNone(md_page)
        pass

    def test_test_get_md_page_properties(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_page = Utils.find_one(page.children, lambda it: it and str(it.title) == "MarkDown Test Page")
        self.assertIsNotNone(md_page)

        md_properties = dict()

        for block in md_page.children:
            if type(block) is CodeBlock:
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
                            md_properties[key] = value

        self.assertTrue(len(md_properties) > 0)
        pass

    def test_test_get_md_page_image(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_page = Utils.find_one(page.children, lambda it: it and str(it.title) == "MarkDown Test Page")
        self.assertIsNotNone(md_page)

        temp_file = ''

        for block in md_page.children:
            if type(block) is ImageBlock:
                image_caption = str(block.caption)
                image_url = str(block.source)
                temp_file = os.path.join(Utils.get_temp_dir(), image_caption + ".jpg")

                print("Download image to : " + temp_file)
                self.__download_file(client, block.id, image_url, temp_file)
                # page = urllib.request.urlopen(image_url)
                # f = open(temp_file, "w")
                # content = page.read()
                # f.write(content)
                # f.close()

        self.assertTrue(os.path.exists(temp_file))
        pass

    def __download_file(self, client, block_id, source, path):

        # "oneliner" helper to safely unwrap lists, see: https://bit.ly/35SUfMK
        unwrap = lambda x: unwrap(next(iter(x), None)) \
            if '__iter__' in dir(x) and not isinstance(x, str) else x

        sources = source
        s3_url = unwrap(sources)
        filename = s3_url.split("/")[-1]

        params = dict(
            table="block",
            id=block_id,
            name=filename,
            download="true",
            userId=client.current_user.id,
            cache="v2",
        )

        url = f"{BASE_URL}signed/" + quote(s3_url, safe="")

        # piggyback off of client's session to proper token is included
        resp = client.session.get(url, params=params, stream=True)

        with open(path, "wb") as fp:
            for chunk in resp.iter_content(chunk_size=1024):
                fp.write(chunk)

