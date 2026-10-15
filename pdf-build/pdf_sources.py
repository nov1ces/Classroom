"""Share opened input PDFs while composing hundreds of source regions."""

import fitz

_DOCUMENTS = {}


def document(path):
    path = str(path)
    if path not in _DOCUMENTS:
        _DOCUMENTS[path] = fitz.open(path)
    return _DOCUMENTS[path]
