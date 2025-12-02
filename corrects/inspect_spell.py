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
        from utils.utils import Utils
        
        self.corrector = None
        self.model_available = False
        self.model_type = None
        
        # Try kenlm-based Corrector first (faster, statistical model)
        if Utils.check_module_installed('kenlm'):
            try:
                from pycorrector import Corrector
                print("Initializing kenlm-based spell checker...")
                self.corrector = Corrector()
                self.model_available = True
                self.model_type = 'kenlm'
                print("kenlm spell checker initialized successfully")
                return
            except Exception as e:
                print(f"Warning: kenlm module found but initialization failed: {e}")
        
        # Fall back to MacBERT model (slower but works without kenlm)
        try:
            from pycorrector import MacBertCorrector
            print("kenlm not available, using MacBERT spell checker (may download model on first use)...")
            self.corrector = MacBertCorrector("shibing624/macbert4csc-base-chinese")
            self.model_available = True
            self.model_type = 'macbert'
            print("MacBERT spell checker initialized successfully")
        except Exception as e:
            print(f"Warning: pycorrector models not available: {e}")
            print("Spell checking will be disabled.")

    def get_name(self):
        if self.model_type == 'kenlm':
            return 'pycorrector_kenlm_inspector'
        elif self.model_type == 'macbert':
            return 'pycorrector_macbert_inspector'
        return 'pycorrector_inspector_disabled'

    def inspect_text(self, text):
        if not self.model_available or not self.corrector:
            return
        try:
            result = self.corrector.correct(text)
            print(result)
        except Exception as e:
            print(f"Error during spell check: {e}")
        pass

    def get_inspect_issues(self, text):
        if not self.model_available or not self.corrector:
            return []
        
        try:
            result = self.corrector.correct(text)
            print(result)
            # Both Corrector and MacBertCorrector return the same format
            # Format: {'source': '...', 'target': '...', 'errors': [('错误词', '正确词', 位置), ...]}
            # Convert to old format: [['错误词', '正确词', start_pos, end_pos], ...]
            if result and 'errors' in result:
                issues = []
                for error in result['errors']:
                    if len(error) >= 3:
                        wrong_word, correct_word, pos = error[0], error[1], error[2]
                        # Calculate end position
                        end_pos = pos + len(wrong_word)
                        issues.append([wrong_word, correct_word, pos, end_pos])
                return issues
        except Exception as e:
            print(f"Error during spell check: {e}")
        
        return []




