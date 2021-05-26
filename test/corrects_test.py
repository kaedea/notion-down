import unittest

from corrects.inspect_spell import PyCorrectorInspector


class CorrectsApiTest(unittest.TestCase):

    def test_pycorrector_spelling_inspect(self):
        text = '少先队员因该为老人让坐'
        PyCorrectorInspector().inspect_text(text)
