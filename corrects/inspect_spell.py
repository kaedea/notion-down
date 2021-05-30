import pycorrector


# noinspection PyMethodMayBeStatic
class SpellInspector:

    def get_name(self):
        return "abs_inspector"

    def inspect_text(self, text):
        raise Exception('Stub!')

    def get_inspect_issues(self, text):
        raise Exception('Stub!')


# noinspection PyMethodMayBeStatic
class PyCorrectorInspector(SpellInspector):
    
    def __init__(self):
        pycorrector.enable_char_error(enable=False)

    def get_name(self):
        return 'pycorrector_inspector'

    def inspect_text(self, text):
        corrected_sent, detail = pycorrector.correct(text)
        print(corrected_sent, detail)
        pass

    def get_inspect_issues(self, text):
        corrected_sent, detail = pycorrector.correct(text)
        print(corrected_sent, detail)
        return detail
