import os
import unittest
from urllib.request import quote

import requests
from notion.block import ImageBlock
from notion.client import NotionClient
from notion.settings import BASE_URL

from notion_writer import ImageDownloader
from utils.utils import Utils, FileUtils


class NotionClientMarkDownPageTest(unittest.TestCase):

    def test_download_youdao_note_image(self):
        url = "https://note.youdao.com/yws/public/resource/ad40842fd256ef2f9998badec2f7e88a/xmlnote/3EAA391F35FF4FF19B060EAD3C93D58F/11830"
        temp_file = FileUtils.new_file(Utils.get_temp_dir(), "temp.jpg")
        print("download file, path = {}, url = {}".format(temp_file, url))
        self.__download_file(url, temp_file)
        pass

    def test_replace_page_image_source(self):
        token = os.environ['NOTION_TOKEN_V2']
        post_url = 'https://www.notion.so/NotionDown-Image-Exchange-2080cb91cb1d47a1bfc9abe9b4710d43'

        client = NotionClient(token_v2=token)
        page = client.get_block(post_url)
        self.assertIsNotNone(page)

        print("The title is:", page.title)
        print("SubPage count = {}", len(page.children))

        md_pages = Utils.find(
            page.children,
            lambda it: it.type == 'page' and 'WIP:' not in str(it.title)
        )
        self.assertIsNotNone(md_pages)

        for md_page in md_pages:
            for block in md_page.children:
                if type(block) is ImageBlock:
                    image_caption = str(block.caption)
                    image_url = str(block.source)
                    if "amazonaws.com" in image_url:
                        print("skip notion image source, url = {}".format(image_url))
                        continue

                    image_downloader = ImageDownloader()
                    path = image_downloader.get_image_path(image_url, image_caption)
                    temp_file = FileUtils.new_file(Utils.get_temp_dir(), path)


                    print("download file, path = {}, url = {}".format(temp_file, image_url))
                    self.__download_file(image_url, temp_file)

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
        pass

    def __download_file(self, source, path):
        r = requests.get(source, allow_redirects=True)  # to get content after redirection
        with open(path, 'wb') as f:
            f.write(r.content)
        pass

    def __download_notion_file(self, client, block_id, source, path):

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
