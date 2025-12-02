import os
import re
import unittest

from config import Config
from notion_reader import NotionReader
from utils.utils import Utils


class PyUtils(unittest.TestCase):
    '''
    Tuning: https://pythex.org/
    '''

    def test_regex_matching(self):
        self.assertIsNotNone(re.compile("^Hello").match('Hello, NotionDown!'))
        self.assertIsNone(re.compile("^NotionDown").match('Hello, NotionDown!'))
        self.assertIsNone(re.compile("\(Hello\)").match('Hello, NotionDown!'))
        self.assertIsNone(re.compile("\(NotionDown\)").match('Hello, NotionDown!'))

    def test_regex_get_letter_idx(self):
        p = re.compile("[a-z]")
        for m in p.finditer('a1b2c3d4'):
            print("start = {}, length = {}, content = {}".format(m.start(), len(m.group()), m.group()))

    def test_regex_get_number_idx(self):
        p = re.compile("[0-9]+")
        for m in p.finditer('0aaaa11b222ccddddd3d4'):
            print("start = {}, length = {}, content = {}".format(m.start(), len(m.group()), m.group()))

    def test_regex_get_markdown_link_idx(self):
        raw_text = '''
        [This is a link](https://respawn.io)
        [This is also a link](https://www.notion.so/kaedea/NotionDown-Obfusing-Blocks-25959a72e55041d6aed69f90226fa45c)
        [This is an obfuscated link]([https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4](https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4))
        ![This is image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T162928Z&X-Amz-Expires=86400&X-Amz-Signature=ae28a9fbf4beb4cf82bf1438c9cbd9f18e2d882aa33874a94bac6cdea09f3f1f&X-Amz-SignedHeaders=host)
        ![This is also an image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host)
        ![This is an obfuscated image]([https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host))
        '''
        p = re.compile("\[.*\]\(.*\)")
        for m in p.finditer(raw_text):
            print("start = {}, length = {}, content = {}".format(m.start(), len(m.group()), m.group()))

    def test_regex_get_markdown_obfuscated_link_idx(self):
        raw_text = '''
        [This is a link](https://respawn.io)
        [This is also a link](https://www.notion.so/kaedea/NotionDown-Obfusing-Blocks-25959a72e55041d6aed69f90226fa45c)
        [This is an obfuscated link]([https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4](https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4))
        ![This is image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T162928Z&X-Amz-Expires=86400&X-Amz-Signature=ae28a9fbf4beb4cf82bf1438c9cbd9f18e2d882aa33874a94bac6cdea09f3f1f&X-Amz-SignedHeaders=host)
        ![This is also an image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host)
        ![This is an obfuscated image]([https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host))
        '''
        obfuscated_links = []
        p = re.compile("\[.*\]\(\[.*\]\(.*\)\)")
        for m in p.finditer(raw_text):
            print("start = {}, length = {}, content = {}".format(m.start(), len(m.group()), m.group()))
            obfuscated_links.append(m.group()[m.group().rfind("](") + len("]("):m.group().rfind("))")])

        print("obfuscated_links = {}".format(obfuscated_links))

    def test_regex_replace_markdown_obfuscated_link_idx(self):
        raw_text = '''
        ## Link Obfuscating
        [This is a link](https://respawn.io)
        [This is also a link](https://www.notion.so/kaedea/NotionDown-Obfusing-Blocks-25959a72e55041d6aed69f90226fa45c)
        [This is an obfuscated link]([https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4](https://www.notion.so/kaedea/MarkDown-Test-Page-9a873436a8b54f6a9b8ec1be725548a4))
        ## Image Obfuscating
        ![This is image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T162928Z&X-Amz-Expires=86400&X-Amz-Signature=ae28a9fbf4beb4cf82bf1438c9cbd9f18e2d882aa33874a94bac6cdea09f3f1f&X-Amz-SignedHeaders=host)
        ![This is also an image](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host)
        ![This is an obfuscated image]([https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/bfcde5f2-47ab-426a-a06d-b1cea91781f4/mmexportd44a4a78d543429542df4e038acffc84_1619870561717.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210515%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210515T101250Z&X-Amz-Expires=86400&X-Amz-Signature=4082b5f128410b128d2da953b8f5b4b719ab1925eb5b6959b66415b0e39492bb&X-Amz-SignedHeaders=host))
        '''
        text = re.sub("\[.*\]\(\[.*\]\(.*\)\)", '{}', raw_text)
        print(text)
        args = ["__LINK__", "__IMAGE__"]
        print(text.format(*args))

    def test_check_module_installed(self):
        self.assertTrue(Utils.check_module_installed("notion"))
        self.assertTrue(Utils.check_module_installed("pangu"))
        self.assertFalse(Utils.check_module_installed("panguxx"))
        self.assertTrue(Utils.check_module_installed("pycorrector"))
        self.assertFalse(Utils.check_module_installed("kenlm"))

