import spacy

_nlp_model = None

def get_nlp_model():
    """
    Loads and returns the spaCy English language model.
    Ensures the model is loaded only once.
    """
    global _nlp_model
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load("en_core_web_sm")
        except OSError:
            print("SpaCy model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
            exit(1)

    return _nlp_model