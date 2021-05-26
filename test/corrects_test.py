import os
import re
import unittest

from config import Config
from corrects.inspect_spell import SpellInspector
from notion_reader import NotionReader
from utils.utils import Utils


class CorrectsApiTest(unittest.TestCase):

    def test_spelling_inspect(self):
        text = '少先队员因该为老人让坐'
        SpellInspector().inspect_text(text)