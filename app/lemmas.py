import pymorphy3

class Lemmatizer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.morph = pymorphy3.MorphAnalyzer()
        return cls._instance
    
    def normalize(self, word: str) -> str:
        
        try:
            parsed = self.morph.parse(word)[0]
            return parsed.normal_form
        except Exception:
            return word.lower()

lemmatizer = Lemmatizer()