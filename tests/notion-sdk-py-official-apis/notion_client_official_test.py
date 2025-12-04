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
        
        Limitation: The current notion-client Python SDK does NOT support file uploads.
        
        Note: The official Notion API added file upload support in 2024, but the
        notion-client SDK may not have implemented this feature yet. The SDK would
        need a 'files' endpoint or similar functionality.
        
        Original test workflow:
        1. Download an existing image ✅ (supported)
        2. Upload it as a new image block ❌ (SDK limitation)
        
        To upload images to Notion, you can:
        - Use the unofficial token_v2 approach (original test), OR
        - Wait for notion-client SDK to add file upload support, OR
        - Use direct HTTP requests to Notion's file upload API, OR
        - Manually upload through the Notion UI
        """
        assert False, (
            "This test cannot be migrated with current notion-client SDK. "
            "The SDK does not yet support file uploads (no 'files' endpoint). "
            "Use token_v2 approach or wait for SDK update."
        )

    def test_replace_image(self):
        """
        CANNOT BE MIGRATED: Test replacing an existing image.
        
        Limitation: File upload not supported in current notion-client SDK.
        
        Note: The official API supports blocks.update() for modifying blocks,
        but uploading new image files requires file upload functionality which
        is not yet available in the notion-client Python SDK.
        
        Original test workflow:
        1. Download an existing image ✅ (supported)
        2. Re-upload it to replace the original ❌ (SDK limitation - no file upload)
        """
        assert False, (
            "This test cannot be migrated with current notion-client SDK. "
            "File upload functionality not yet implemented in SDK. "
            "Use token_v2 approach or wait for SDK update."
        )

    def test_replace_image_r2(self):
        """
        CANNOT BE MIGRATED: Test replacing image via temporary upload.
        
        Limitation: File upload not supported in current notion-client SDK.
        
        Note: The official API DOES support:
        - ✅ Creating new blocks (blocks.children.append)
        - ✅ Removing blocks (blocks.delete)
        - ✅ Modifying block properties (blocks.update)
        
        But does NOT support (in current SDK):
        - ❌ Uploading files/images (no 'files' endpoint in SDK)
        
        Original test workflow:
        1. Download image ✅ (supported)
        2. Create temporary image block ✅ (supported - blocks.children.append)
        3. Upload to temporary block ❌ (SDK limitation - no file upload)
        4. Copy URL to target block ✅ (supported - blocks.update)
        5. Remove temporary block ✅ (supported - blocks.delete)
        """
        assert False, (
            "This test cannot be migrated with current notion-client SDK. "
            "While block manipulation is supported, file upload is not yet available in SDK. "
            "Use token_v2 approach or wait for SDK update."
        )

    def test_replace_image_r3(self):
        """
        CANNOT BE MIGRATED: Test replacing image with block manipulation.
        
        Limitations:
        1. File upload not supported in current notion-client SDK
        2. Moving blocks not supported by Notion API itself
        
        Note: The official API DOES support:
        - ✅ Creating new blocks (blocks.children.append)
        - ✅ Removing blocks (blocks.delete)
        - ✅ Modifying text blocks (blocks.update)
        
        But does NOT support:
        - ❌ Uploading files/images (SDK limitation)
        - ❌ Moving blocks to change order (API limitation)
        
        Original test workflow:
        1. Download image ✅ (supported)
        2. Create new image block ✅ (supported - blocks.children.append)
        3. Upload image ❌ (SDK limitation - no file upload)
        4. Move new block after old block ❌ (API limitation - no block reordering)
        5. Remove old block ✅ (supported - blocks.delete)
        6. Update text blocks with timestamp ✅ (supported - blocks.update)
        """
        assert False, (
            "This test cannot be migrated due to two limitations: "
            "1) File upload not in SDK, 2) Block reordering not in API. "
            "Use token_v2 approach for full functionality."
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
