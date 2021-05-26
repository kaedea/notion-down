import pycorrector


# noinspection PyMethodMayBeStatic
class SpellInspector:

    def inspect_text(self, text):
        raise Exception('Stub!')


class PyCorrectorInspector(SpellInspector):

    def inspect_text(self, text):
        corrected_sent, detail = pycorrector.correct(text)
        print(corrected_sent, detail)
        pass
