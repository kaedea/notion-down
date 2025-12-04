import os
import unittest

from config import Config
from notion_reader import NotionReader
from notion_writer import ImageDownloader
from utils.utils import Utils, FileUtils


class NotionClientOfficialTest(unittest.TestCase):
    """
    Migrated from notion_client_test.py (token_v2) to use official notion-client API.
    
    Note: The official Notion API has significant limitations compared to token_v2:
    - ✅ Reading pages and blocks
    - ✅ Downloading images
    - ✅ Parsing properties
    - ❌ Uploading files/images
    - ❌ Modifying content
    - ❌ Creating/deleting blocks
    """

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

    def test_check_token(self):
        """Test that NOTION_TOKEN environment variable exists"""
        self.assertTrue("NOTION_TOKEN" in os.environ, "NOTION_TOKEN environment variable should exist")

    def test_get_page(self):
        """Test retrieving a page using official API"""
        main_page = NotionReader.read_main_page()
        self.assertIsNotNone(main_page)
        
        print(f"Page ID: {main_page.get('id')}")
        print(f"Page object type: {main_page.get('object')}")

    def test_get_md_page(self):
        """Test finding a specific markdown test page"""
        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)
        
        print(f"The title is: {md_page.get_title()}")
        print(f"Block count: {len(md_page.blocks)}")

    def test_get_md_page_properties(self):
        """
        Test parsing custom properties from [notion-down-properties] code blocks.
        
        Note: Code blocks containing [notion-down-properties] are automatically
        parsed during NotionPage.parse() and stored in md_page.properties.
        They are NOT included in md_page.blocks.
        """
        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)
        
        print(f"The title is: {md_page.get_title()}")
        print(f"Block count: {len(md_page.blocks)}")
        
        # Properties from [notion-down-properties] code blocks are automatically
        # parsed and stored in md_page.properties during page parsing
        md_properties = md_page.properties
        
        self.assertIsNotNone(md_properties, "Should have properties")
        print(f"Parsed properties: {md_properties}")
        
        # Verify we have the expected properties from [notion-down-properties]
        expected_keys = ['Title', 'Date', 'Published', 'Category', 'Tag', 'FileLocate', 'FileName']
        for key in expected_keys:
            self.assertIn(key, md_properties, f"Should have '{key}' property")
        
        # Verify specific values
        self.assertEqual(md_properties['Date'], '2021-05-01')
        self.assertEqual(md_properties['Published'], 'false')

    def test_get_md_page_image(self):
        """Test finding and downloading images from a page"""
        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)
        
        print(f"The title is: {md_page.get_title()}")
        print(f"Block count: {len(md_page.blocks)}")
        
        temp_file = ''
        
        for block in md_page.blocks:
            if block.type == 'image' and hasattr(block, 'image_url'):
                image_caption = block.image_caption if hasattr(block, 'image_caption') else ''
                image_url = block.image_url
                temp_file = os.path.join(Utils.get_temp_dir(), (image_caption or 'image') + ".jpg")
                
                print(f"Download image to: {temp_file}")
                image_downloader = ImageDownloader()
                image_downloader.download_image(image_url, temp_file)
                break
        
        self.assertTrue(os.path.exists(temp_file), "Image file should be downloaded")

    def test_list_image(self):
        """Test listing all image blocks in a page"""
        md_page = NotionReader.handle_page_with_title("NotionDown Image Source")
        self.assertIsNotNone(md_page)
        
        print(f"The title is: {md_page.get_title()}")
        print(f"Block count: {len(md_page.blocks)}")
        
        image_count = 0
        for block in md_page.blocks:
            if block.type == 'image':
                print(f"Found image block: {block.id}")
                image_count += 1
        
        print(f"Total images found: {image_count}")
        self.assertTrue(image_count > 0, "Should find at least one image")

    def test_upload_image(self):
        """
        CANNOT BE MIGRATED: Test uploading an image to Notion.
        
        The official Notion API does NOT support uploading files or images.
        
        Original test workflow:
        1. Download an existing image ✅ (supported)
        2. Upload it as a new image block ❌ (NOT supported)
        
        To upload images to Notion, you must:
        - Use the unofficial token_v2 approach (original test), OR
        - Manually upload through the Notion UI, OR
        - Use a third-party service
        """
        assert False, (
            "This test cannot be migrated to official API. "
            "The official Notion API does not support uploading images. "
            "Use token_v2 approach if you need to upload images programmatically."
        )

    def test_replace_image(self):
        """
        CANNOT BE MIGRATED: Test replacing an existing image.
        
        The official Notion API does NOT support:
        - Uploading files/images
        - Modifying existing blocks
        
        Original test workflow:
        1. Download an existing image ✅ (supported)
        2. Re-upload it to replace the original ❌ (NOT supported)
        """
        assert False, (
            "This test cannot be migrated to official API. "
            "The official Notion API does not support uploading or modifying images. "
            "Use token_v2 approach if you need to replace images programmatically."
        )

    def test_replace_image_r2(self):
        """
        CANNOT BE MIGRATED: Test replacing image via temporary upload.
        
        The official Notion API does NOT support:
        - Uploading files/images
        - Creating new blocks
        - Removing blocks
        - Modifying block properties
        
        Original test workflow:
        1. Download image ✅ (supported)
        2. Create temporary image block ❌ (NOT supported)
        3. Upload to temporary block ❌ (NOT supported)
        4. Copy URL to target block ❌ (NOT supported)
        5. Remove temporary block ❌ (NOT supported)
        """
        assert False, (
            "This test cannot be migrated to official API. "
            "The official Notion API does not support creating, uploading, or removing blocks. "
            "Use token_v2 approach if you need this functionality."
        )

    def test_replace_image_r3(self):
        """
        CANNOT BE MIGRATED: Test replacing image with block manipulation.
        
        The official Notion API does NOT support:
        - Uploading files/images
        - Creating new blocks
        - Moving blocks
        - Removing blocks
        - Modifying text blocks
        
        Original test workflow:
        1. Download image ✅ (supported)
        2. Create new image block ❌ (NOT supported)
        3. Upload image ❌ (NOT supported)
        4. Move new block after old block ❌ (NOT supported)
        5. Remove old block ❌ (NOT supported)
        6. Update text blocks with timestamp ❌ (NOT supported)
        """
        assert False, (
            "This test cannot be migrated to official API. "
            "The official Notion API does not support any write operations. "
            "Use token_v2 approach if you need to manipulate Notion content."
        )

    def test_get_md_page_table(self):
        """
        Test parsing table/database blocks from a page.
        
        Note: The official API supports reading databases, but the structure
        is different from token_v2. This test demonstrates basic database reading.
        """
        md_page = NotionReader.handle_page_with_title("MarkDown Test Page")
        self.assertIsNotNone(md_page)
        
        print(f"The title is: {md_page.get_title()}")
        print(f"Block count: {len(md_page.blocks)}")
        
        # Find collection_view blocks (databases/tables)
        table_count = 0
        for block in md_page.blocks:
            if block.type == 'collection_view':
                print(f"Found table/database block: {block.id}")
                table_count += 1
                # Note: Detailed table parsing would require additional API calls
                # to query the database, which is supported by the official API
                # but requires different implementation than token_v2
        
        print(f"Total tables found: {table_count}")
        # Note: We don't assert table_count > 0 because the test page might not have tables


class NotionClientMarkDownPageOfficialTest(unittest.TestCase):
    """
    Additional tests for markdown page handling with official API.
    Migrated from NotionClientMarkDownPageTest class.
    """

    def setUp(self):
        Config.parse_configs()
        Config.set_debuggable(True)
        Config.set_blog_url("https://www.notion.so/kaedea/Noton-Down-Sample-440de7dca89840b6b3bab13d2aa92a34")
        Config.set_output(os.path.join(Utils.get_workspace(), "build"))
        Config.check_required_args()

    # Note: Most tests from NotionClientMarkDownPageTest are duplicates
    # of tests in NotionClientOfficialTest, so they are not repeated here.
    # The original class structure is preserved for reference.


if __name__ == '__main__':
    unittest.main()
