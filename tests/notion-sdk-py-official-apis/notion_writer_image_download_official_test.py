import os
import unittest

from config import Config
from notion_page import PageImageBlock, PageTextBlock
from notion_reader import NotionReader
from notion_writer import NotionWriter, ImageDownloader
from utils.utils import Utils, FileUtils


class NotionWriterImageDownloadOfficialTest(unittest.TestCase):
    """
    Migrated from notion_writer_image_download_test.py (token_v2) to use official notion-client API.
    
    Note: This test file focuses on image download functionality which is supported by the official API.
    Tests that required uploading images to Notion have been removed as the official API does not support uploads.
    """

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

    def test_get_image_path(self):
        """Test ImageDownloader.get_image_path() utility function"""
        image_downloader = ImageDownloader()
        image_url = "https://www.notion.so/kaedea/mock-image-url.jpg"
        image_caption = "Image Caption"
        path = image_downloader.get_image_path(image_url, image_caption)
        self.assertEqual('image_caption_mock_image_url.jpg', path.lower())

        image_url = "https://www.notion.so/kaedea/mock-image-url.jpg"
        image_caption = None
        path = image_downloader.get_image_path(image_url, image_caption)
        self.assertEqual('mock_image_url.jpg', path.lower())

        image_url = "https://www.notion.so/kaedea/mock-image-url.jpg?xxx"
        image_caption = "Image Caption"
        path = image_downloader.get_image_path(image_url, image_caption)
        self.assertEqual('image_caption_mock_image_url.jpg', path.lower())

    def test_get_image_path_for_notion(self):
        """Test ImageDownloader.get_image_path() with Notion S3 URLs"""
        image_downloader = ImageDownloader()
        image_url = "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/4dcaf5d8-79f9-40e1-b58f-f5044b852a03/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210804%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210804T073203Z&X-Amz-Expires=86400&X-Amz-Signature=16cac0ae0546846762c4a5b628dcd88f6332a03507ac0c130e6c5390accfa657&X-Amz-SignedHeaders=host"
        image_caption = ""
        path = image_downloader.get_image_path(image_url, image_caption)
        self.assertEqual('4dcaf5d8_79f9_40e1_b58f_f5044b852a03_untitled.png', path.lower())

        image_url = "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/8e770ef6-890e-406f-ba93-69f634d2b753/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210804%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210804T073203Z&X-Amz-Expires=86400&X-Amz-Signature=fd6b436fae796f587653b36c35dd6a8632c2ded38e636d54e762caf85d41619d&X-Amz-SignedHeaders=host"
        image_caption = None
        path = image_downloader.get_image_path(image_url, image_caption)
        self.assertEqual('8e770ef6_890e_406f_ba93_69f634d2b753_untitled.png', path.lower())

        image_url = "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/19e02336-b567-42a8-8bff-b5b8a9d0f361/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210804%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210804T073204Z&X-Amz-Expires=86400&X-Amz-Signature=8adf045b785ca4c638248e505c0b42a7af103732b2c2b2dd670ee9101ae69220&X-Amz-SignedHeaders=host"
        image_caption = ""
        path = image_downloader.get_image_path(image_url, image_caption)
        self.assertEqual('19e02336_b567_42a8_8bff_b5b8a9d0f361_untitled.png', path.lower())

    def test_need_download_image(self):
        """Test ImageDownloader.need_download_image() logic"""
        image_downloader = ImageDownloader()
        self.assertFalse(image_downloader.need_download_image(PageTextBlock()))
        Config.set_download_image(False)
        self.assertFalse(image_downloader.need_download_image(PageImageBlock()))
        Config.set_download_image(True)
        self.assertFalse(image_downloader.need_download_image(PageImageBlock()))
        block = PageImageBlock()
        block.image_url = "https://circleci.com/gh/kaedea/notion-down.svg?style=shield&circle-token=9f4dc656e94d8deccd362e52400c96e709c7e8b3"
        self.assertTrue(image_downloader.need_download_image(block))
        block.image_url = "https://circleci.com/gh/kaedea/notion-down.svg?style=shield&circle-token=9f4dc656e94d8deccd362e52400c96e709c7e8b3&keep-url-source=true"
        self.assertFalse(image_downloader.need_download_image(block))

    def test_download_image(self):
        """
        Test downloading images from a Notion page using official API.
        
        Note: This test uses the official notion-client API to retrieve the page,
        then downloads images using standard HTTP requests (not Notion-specific).
        """
        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)

        # Find image blocks
        image_blocks = [block for block in md_page.blocks if block.type == 'image']
        self.assertTrue(len(image_blocks) > 0, "Should have at least one image block")

        # Test downloading first image
        for block in image_blocks:
            if hasattr(block, 'image_url') and block.image_url:
                image_caption = block.image_caption if hasattr(block, 'image_caption') else ''
                image_url = block.image_url

                image_downloader = ImageDownloader()
                path = image_downloader.get_image_path(image_url, image_caption)
                temp_file = FileUtils.new_file(Utils.get_temp_dir(), path)

                print(f"Download image to: {temp_file}")
                image_downloader.download_image(image_url, temp_file)
                
                self.assertTrue(os.path.exists(temp_file))
                break

    def test_handle_write_markdown_test_page(self):
        """Test writing markdown page with image download enabled"""
        Config.set_download_image(True)
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)

    def test_handle_write_markdown_readme_page(self):
        """Test writing README page with image download enabled"""
        Config.set_download_image(True)
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown README")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)

    def test_handle_write_markdown_column_list_page(self):
        """Test writing page with column list blocks and image download enabled"""
        Config.set_download_image(True)
        NotionWriter.clean_output()

        md_page = NotionReader.handle_page_with_title("NotionDown Pullquote Blocks")
        self.assertIsNotNone(md_page)

        NotionWriter.handle_page(md_page)


if __name__ == '__main__':
    unittest.main()
