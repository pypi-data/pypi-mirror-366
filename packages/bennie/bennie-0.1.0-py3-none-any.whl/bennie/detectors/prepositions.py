from ..core import get_nlp_model

def find_dangling_prepositions(text: str) -> tuple[bool, list[str]]:
    """
    Detects dangling prepositions in the given text.

    Args:
        text (str): The input text, which can be an English sentence or multiple sentences.

    Returns:
        tuple[bool, list[str]]: A tuple where the first element is True if any
        dangling prepositions are detected, False otherwise. The second element
        is a list of sentences (or clauses) where dangling prepositions were found.
    """
    nlp = get_nlp_model()
    doc = nlp(text)
    dangling_found = False
    sentences_with_dangling = []

    for sent in doc.sents:
        has_dangling_in_sentence = False
        tokens = [token for token in sent if not token.is_punct]

        for i, token in enumerate(tokens):
            if token.pos_ == "ADP":
                is_last_word = (i == len(tokens) - 1)

                if is_last_word:
                    has_dangling_in_sentence = True
                    break

                found_pobj = False
                for child in token.children:
                    if child.dep_ == "pobj":
                        found_pobj = True
                        break

                if not found_pobj and not is_last_word:
                    pass

        if has_dangling_in_sentence:
            dangling_found = True
            sentences_with_dangling.append(sent.text)

    return dangling_found, sentences_with_dangling