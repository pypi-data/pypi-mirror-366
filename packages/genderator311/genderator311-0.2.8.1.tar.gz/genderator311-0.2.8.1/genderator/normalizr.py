import re
import unicodedata
from unidecode import unidecode

class Normalizr:
    def __init__(self, lang="es"):
        self.lang = lang

    def normalize(self, text, steps=None):
        # Replaces hyphens with space
        text = re.sub(r"[-‐‑‒–—―]", " ", text)

        # Replace symbols with normalized unicode forms
        text = unicodedata.normalize("NFKC", text)

        # Remove punctuation except basic name characters
        text = re.sub(r"[^\w\sñÑçÇ']", "", text)

        # Remove extra whitespace
        text = " ".join(text.split())

        # Remove accent marks
        text = unidecode(text)

        return text
