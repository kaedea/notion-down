import unittest

from notion_page import PageTextBlock


class NotionPageTest(unittest.TestCase):

    def test_parse_text_block_with_obfuscated_links(self):
        block = PageTextBlock()
        block.text = '''
        ## Link Obfuscating
        [This is a link](https://respawn.io)
        [This is also a link](https://www.notion.so/kaedea/NotionDown-Obfusing-Blocks-25959a72e55041d6aed69f90226fa45c)
        [This is an obfuscated link]([https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4](https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4))
        ## Image Obfuscating
        ![This is image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T162928Z&X-Amz-Expires=86400&X-Amz-Signature=ae28a9fbf4beb4cf82bf1438c9cbd9f18e2d882aa33874a94bac6cdea09f3f1f&X-Amz-SignedHeaders=host)
        ![This is also an image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host)
        ![This is an obfuscated image]([https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host))
        '''

        block_text = block.write_block()
        print(block_text)

        self.assertEqual('''
        ## Link Obfuscating
        [This is a link](https://respawn.io)
        [This is also a link](https://www.notion.so/kaedea/NotionDown-Obfusing-Blocks-25959a72e55041d6aed69f90226fa45c)
        [This is an obfuscated link](https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4)
        ## Image Obfuscating
        ![This is image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T162928Z&X-Amz-Expires=86400&X-Amz-Signature=ae28a9fbf4beb4cf82bf1438c9cbd9f18e2d882aa33874a94bac6cdea09f3f1f&X-Amz-SignedHeaders=host)
        ![This is also an image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host)
        ![This is an obfuscated image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host)
        ''', block_text)


