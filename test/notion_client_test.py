import datetime
import os
import unittest

from urllib.request import quote
from notion.block import CodeBlock, ImageBlock, CollectionViewBlock, DividerBlock, TextBlock
from notion.client import NotionClient
from notion.collection import Collection
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

    def test_list_image(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_page = Utils.find_one(
            page.children,
            lambda it: it.type == 'page' and str(it.title) == "NotionDown Image Source"
        )
        self.assertIsNotNone(md_page)

        for block in md_page.children:
            if type(block) is ImageBlock:
                print("get image block: {}".format(block))
        pass

    def test_upload_image(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_page = Utils.find_one(
            page.children,
            lambda it: it.type == 'page' and str(it.title) == "NotionDown Image Source"
        )
        self.assertIsNotNone(md_page)

        temp_file = ''

        for block in md_page.children:
            if type(block) is ImageBlock:
                image_caption = str(block.caption)
                image_url = str(block.source)
                temp_file = os.path.join(Utils.get_temp_dir(), image_caption + ".jpg")

                print("Download image to : " + temp_file)
                self.__download_file(client, block.id, image_url, temp_file)
                break

        self.assertTrue(os.path.exists(temp_file))

        count = len([it for it in md_page.children if type(it) is ImageBlock])
        print("Image count = {}".format(count))

        print("Upload new image {}".format(count + 1))
        new_image_block = md_page.children.add_new(
            ImageBlock,
            caption="Image {}".format(count + 1),
            width=800
        )
        new_image_block.upload_file(temp_file)
        pass

    def test_replace_image(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_page = Utils.find_one(page.children,
                                 lambda it: it.type == 'page' and str(it.title) == "NotionDown Image Source")
        self.assertIsNotNone(md_page)

        for block in md_page.children:
            if type(block) is ImageBlock:
                image_caption = str(block.caption)
                image_url = str(block.source)
                temp_file = os.path.join(Utils.get_temp_dir(), image_caption + ".jpg")

                print("Download image to : " + temp_file)
                self.__download_file(client, block.id, image_url, temp_file)

                self.assertTrue(os.path.exists(temp_file))

                print("Upload image file : " + temp_file)
                block.upload_file(temp_file)
                new_url = str(block.source)
                print("Get new image url : " + new_url)
                break

        pass

    def test_replace_image_r2(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_page = Utils.find_one(page.children,
                                 lambda it: it.type == 'page' and str(it.title) == "NotionDown Image Source")
        self.assertIsNotNone(md_page)

        for block in md_page.children:
            if type(block) is ImageBlock:
                image_caption = str(block.caption)
                image_url = str(block.source)
                temp_file = os.path.join(Utils.get_temp_dir(), image_caption + ".jpg")

                print("Download image to : " + temp_file)
                self.__download_file(client, block.id, image_url, temp_file)

                self.assertTrue(os.path.exists(temp_file))

                print("Upload image file : " + temp_file)
                temp_image = md_page.children.add_new(ImageBlock, caption="temp image", width=800)
                temp_image.upload_file(temp_file)
                new_url = str(temp_image.source)
                print("Get new image url : " + new_url)
                temp_image.remove()  # this will cause new_url become 404
                block.source = new_url
                break

        pass

    def test_replace_image_r3(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_page = Utils.find_one(
            page.children,
            lambda it: it.type == 'page' and str(it.title) == "NotionDown Image Source"
        )
        self.assertIsNotNone(md_page)

        new_url = None

        for block in md_page.children:
            if type(block) is ImageBlock:
                image_caption = str(block.caption)
                image_url = str(block.source)
                temp_file = os.path.join(Utils.get_temp_dir(), image_caption + ".jpg")

                print("Download image to : " + temp_file)
                self.__download_file(client, block.id, image_url, temp_file)

                self.assertTrue(os.path.exists(temp_file))

                print("Upload image file : " + temp_file)
                new_image_block = md_page.children.add_new(
                    ImageBlock,
                    caption=block.caption,
                    width=block.width,
                    full_width=block.full_width,
                    page_width=block.page_width,
                )
                new_image_block.upload_file(temp_file)
                new_url = str(new_image_block.source)
                print("Get new image url : " + new_url)
                new_image_block.move_to(block, "after")
                block.remove()
                continue

            if type(block) is TextBlock:
                if 'Updated:' in block.title:
                    block.title = "Updated: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    pass
                elif 'Image source was replacing to:' in block.title:
                    block.title = 'Image source was replacing to: [{}]({})'.format(new_url, new_url)
                    pass
                continue

            if type(block) is DividerBlock:
                break

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

    def test_test_get_md_page_table(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_page = Utils.find_one(page.children, lambda it: it and str(it.title) == "MarkDown Test Page")
        self.assertIsNotNone(md_page)

        for block in md_page.children:
            if block.type == 'collection_view':
                self.__dump_collection(block)

    def __dump_collection(self, block: CollectionViewBlock):
        column_properties = block.collection.get_schema_properties()
        ordered_column_ids = block.views[0].get("format.table_properties")

        ordered_column_properties = []
        for id in ordered_column_ids:
            ordered_column_properties.append(Utils.find_one(
                column_properties,
                lambda it: it['id'] == id['property']
            ))

        slugs = [it['slug'] for it in ordered_column_properties]
        types = [it['type'] for it in ordered_column_properties]

        print("{}".format(" | ".join([it['name'] for it in ordered_column_properties])))
        print("{}".format(" | ".join([':---:' for it in ordered_column_properties])))

        for row in block.collection.get_rows():
            contents = []
            for idx, slug in enumerate(slugs):
                item_type = types[idx]
                item_value = getattr(row, slug)
                contents.append(self.__parse_collection_item(item_type, item_value))
            print("{}".format(" | ".join(contents)))
        pass


    def __parse_collection_item(self, collection_type, item):
        if not item:
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
            # https://s3.us-west-2.amazonaws.com/secure.notion-static.com/a88e9b90-8865-4cfb-bdf9-c614f5a05ce0/AptioFix-R24-RELEASE.zip?\
            # X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210506%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210506T172606Z&\
            # X-Amz-\Expires=86400&X-Amz-Signature=a2a9c71829809cf224762400de378d277715f76b910d806573806c7881ba9b4b&X-Amz-SignedHeaders=host
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




