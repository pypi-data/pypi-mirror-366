
INFLECTIONS = [
    {"suffix": "ن",        "gender": None,       "number": "plural",     "person": None},
    {"suffix": "نا",       "gender": None,       "number": "singular",   "person": None},
    {"suffix": "نے",       "gender": None,       "number": "singular",   "person": "third"},
    {"suffix": "دا",       "gender": "masculine","number": "singular",   "person": "third"},
    {"suffix": "دی",       "gender": "feminine", "number": "singular",   "person": "third"},
    {"suffix": "دے",       "gender": "masculine","number": "plural",     "person": "third"},
    {"suffix": "دیاں",     "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "دِیاں",    "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "و",        "gender": None,       "number": None,         "person": "second"},
    {"suffix": "اں",       "gender": None,       "number": "plural",     "person": "first"},
    {"suffix": "یے",       "gender": None,       "number": "plural",     "person": "second"},
    {"suffix": "یں",       "gender": "feminine", "number": "plural",     "person": "second"},
    {"suffix": "یِں",      "gender": "feminine", "number": "plural",     "person": "second"},
    {"suffix": "یو",       "gender": None,       "number": "plural",     "person": "second"},
    {"suffix": "یا",       "gender": "masculine","number": "singular",   "person": "third"},
    {"suffix": "نی",       "gender": "feminine", "number": "singular",   "person": "third"},
    {"suffix": "ی",        "gender": None,       "number": None,         "person": None},
    {"suffix": "نیاں",     "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "یاں",      "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "یِاں",     "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "ے",        "gender": "masculine","number": "plural",     "person": "third"},
    {"suffix": "ا",        "gender": "masculine","number": "singular",   "person": "third"},
    {"suffix": "ان",       "gender": "masculine","number": "plural",     "person": "third"},
    {"suffix": "انا",      "gender": "masculine","number": "singular",   "person": None},
    {"suffix": "انے",      "gender": "masculine","number": "plural",     "person": None},
    {"suffix": "اندا",     "gender": "masculine","number": "singular",   "person": "third"},
    {"suffix": "اندی",     "gender": "feminine", "number": "singular",   "person": "third"},
    {"suffix": "اندے",     "gender": "masculine","number": "plural",     "person": "third"},
    {"suffix": "اندیاں",   "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "اندِیاں",  "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "ائو",      "gender": None,       "number": "plural",     "person": "second"},
    {"suffix": "اواں",     "gender": None,       "number": "plural",     "person": "first"},
    {"suffix": "ائیے",     "gender": None,       "number": "plural",     "person": "second"},
    {"suffix": "ائیں",     "gender": "feminine", "number": "plural",     "person": "second"},
    {"suffix": "ائیِں",    "gender": "feminine", "number": "plural",     "person": "second"},
    {"suffix": "ایو",      "gender": None,       "number": "plural",     "person": "second"},
    {"suffix": "ایا",      "gender": "masculine","number": "singular",   "person": "third"},
    {"suffix": "انی",      "gender": "feminine", "number": "singular",   "person": "third"},
    {"suffix": "ائی",      "gender": "feminine", "number": "singular",   "person": "third"},
    {"suffix": "انیاں",    "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "ایاں",     "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "ایِاں",    "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "اے",       "gender": None,       "number": "singular",   "person": "second"},
    {"suffix": "وا",       "gender": "masculine","number": "singular",   "person": "third"},
    {"suffix": "وان",      "gender": "masculine","number": "plural",     "person": "third"},
    {"suffix": "وانا",     "gender": "masculine","number": "singular",   "person": None},
    {"suffix": "وانے",     "gender": "masculine","number": "plural",     "person": None},
    {"suffix": "واندا",    "gender": "masculine","number": "singular",   "person": "third"},
    {"suffix": "واندی",    "gender": "feminine", "number": "singular",   "person": "third"},
    {"suffix": "واندے",    "gender": "masculine","number": "plural",     "person": "third"},
    {"suffix": "واندیاں",  "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "واندِیاں", "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "وائو",     "gender": None,       "number": "plural",     "person": "second"},
    {"suffix": "واواں",    "gender": None,       "number": "plural",     "person": "first"},
    {"suffix": "وائیے",    "gender": None,       "number": "plural",     "person": "second"},
    {"suffix": "وائیں",    "gender": "feminine", "number": "plural",     "person": "second"},
    {"suffix": "وائیِں",   "gender": "feminine", "number": "plural",     "person": "second"},
    {"suffix": "وایو",     "gender": None,       "number": "plural",     "person": "second"},
    {"suffix": "وایا",     "gender": "masculine","number": "singular",   "person": "third"},
    {"suffix": "وانی",     "gender": "feminine", "number": "singular",   "person": "third"},
    {"suffix": "وائی",     "gender": "feminine", "number": "singular",   "person": "third"},
    {"suffix": "وانیاں",   "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "وانیِاں",  "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "وائیِاں",  "gender": "feminine", "number": "plural",     "person": "third"},
    {"suffix": "واے",      "gender": None,       "number": "singular",   "person": "second"}
]


class PunjabiInflector:
    def __init__(self, inflections=None):
        self.inflections = inflections or INFLECTIONS

    def inflect(self, root):
        """Generate all inflected forms of the root word."""
        return [root + i["suffix"] for i in self.inflections]

    def is_valid_inflection(self, word, root):
        """Check if a given word is a valid inflection of the root."""
        return any(word == root + i["suffix"] for i in self.inflections)

    def get_suffix(self, word, root):
        """Return the suffix if the word is a valid inflection of root."""
        for i in self.inflections:
            if word == root + i["suffix"]:
                return i["suffix"]
        return None

    def get_metadata(self, word, root):
        """Return full metadata if valid inflection is found."""
        for i in self.inflections:
            if word == root + i["suffix"]:
                return i
        return None