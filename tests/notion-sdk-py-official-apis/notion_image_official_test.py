import os
import unittest

import requests
from notion_writer import ImageDownloader
from utils.utils import Utils, FileUtils


class NotionImageOfficialTest(unittest.TestCase):
    """
    Migrated from notion_image_replace_test.py (token_v2) to use official notion-client API.
    
    Note: The official Notion API does NOT support:
    - Uploading images to Notion
    - Modifying/replacing existing blocks
    - Creating new blocks
    
    Therefore, only download-related tests can be fully migrated.
    Tests requiring upload/modification are included as stubs with explanations.
    """

    def test_download_youdao_note_image(self):
        """
        Test downloading an external image (not from Notion).
        
        This test doesn't require Notion API at all, so it works identically
        with both token_v2 and official API approaches.
        """
        url = "https://note.youdao.com/yws/public/resource/ad40842fd256ef2f9998badec2f7e88a/xmlnote/3EAA391F35FF4FF19B060EAD3C93D58F/11830"
        temp_file = FileUtils.new_file(Utils.get_temp_dir(), "temp.jpg")
        print(f"download file, path = {temp_file}, url = {url}")
        self._download_file(url, temp_file)
        
        # Verify file was downloaded
        self.assertTrue(os.path.exists(temp_file))

    def test_replace_page_image_source(self):
        """
        CANNOT BE MIGRATED: Test replacing image sources in Notion pages.
        
        This test cannot be migrated to the official API because:
        1. The official API does NOT support uploading files/images to Notion
        2. The official API does NOT support modifying existing blocks
        3. The official API does NOT support creating new blocks
        4. The official API does NOT support moving or removing blocks
        
        Original test workflow:
        1. Read pages from Notion ✅ (supported)
        2. Find image blocks ✅ (supported)
        3. Download images from external URLs ✅ (supported)
        4. Upload images to Notion ❌ (NOT supported)
        5. Replace old image blocks with new ones ❌ (NOT supported)
        
        The official Notion API is read-only for content. To perform image
        replacement, you would need to:
        - Use the unofficial token_v2 approach (original test), OR
        - Manually update images through the Notion UI, OR
        - Use a third-party service that supports Notion modifications
        """
        assert False, (
            "This test cannot be migrated to official API. "
            "The official Notion API does not support uploading images or modifying blocks. "
            "Use token_v2 approach (original test) if you need to replace images programmatically."
        )

    def _download_file(self, source, path):
        """Helper method to download a file from a URL"""
        r = requests.get(source, allow_redirects=True)
        with open(path, 'wb') as f:
            f.write(r.content)


if __name__ == '__main__':
    unittest.main()
