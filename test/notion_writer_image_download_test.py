import os
import requests
import unittest

from notion.block import ImageBlock
from notion.client import NotionClient

from config import Config
from notion_reader import NotionReader
from notion_writer import NotionWriter, ImageDownloader
from utils.utils import Utils, FileUtils


class NotionWriterImageDownloadTest(unittest.TestCase):

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

    def test_get_image_path(self):
        image_downloader = ImageDownloader()
        image_url = "https://www.notion.so/kaedea/mock-image-url.jpg"
        image_caption = "Image Caption"
        path = image_downloader.get_image_path(image_url, image_caption)
        self.assertTrue(path.lower() == 'image_caption_mock_image_url_jpg')

        image_url = "https://www.notion.so/kaedea/mock-image-url.jpg"
        image_caption = None
        path = image_downloader.get_image_path(image_url, image_caption)
        self.assertTrue(path.lower() == 'mock_image_url_jpg')

        image_url = "https://www.notion.so/kaedea/mock-image-url.jpg?xxx"
        image_caption = "Image Caption"
        path = image_downloader.get_image_path(image_url, image_caption)
        self.assertTrue(path.lower() == 'image_caption_mock_image_url_jpg')
        pass

    def test_download_image(self):
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

                image_downloader = ImageDownloader()
                path = image_downloader.get_image_path(image_url, image_caption)
                temp_file = FileUtils.new_file(Utils.get_temp_dir(), path)

                print("Download image to : " + temp_file)
                image_downloader.download_image(image_url, temp_file)
                break

        self.assertTrue(os.path.exists(temp_file))
        pass

    def test_handle_write_markdown_test_page(self):
        Config.set_download_image(True)
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

    def test_handle_write_markdown_readme_page(self):
        Config.set_download_image(True)
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown README")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)
        pass

