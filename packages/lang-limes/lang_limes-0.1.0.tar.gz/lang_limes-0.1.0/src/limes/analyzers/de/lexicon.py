import importlib.resources

from marisa_trie import RecordTrie

from limes.analyzers.interfaces import Lexicon


class GermanLexicon(Lexicon):
    """
    Class for retrieving information regarding word frequency and lexicon
    membership. Concrete implementations might also serve as interfaces for
    language-specific lexical resources such as word groups and affixes.
    """

    def __init__(self):
        self._data: RecordTrie | None = None

    def contains(self, word: str) -> bool:
        """Check whether the given word is contained in the lexicon."""
        data = self._ensure_data_loaded()
        return word in data

    def get_frequency_score(self, word: str) -> float | None:
        """
        Identify how frequent a given word is in the given Lexicon. Please note
        that frequency is described in relative terms, normalized to [0.0, 1.0].
        """
        data = self._ensure_data_loaded()
        match = data.get(word)
        # As the trie returs lists of tuples, we have to unwrap None results.
        if match is not None:
            match = match[0][0]
        return match

    def _ensure_data_loaded(self) -> RecordTrie:
        """
        Load data into cache if it hasn't been loaded before, and return it.
        """
        if self._data is None:
            self._data = self._load_data_file()
        return self._data

    @staticmethod
    def _load_data_file() -> RecordTrie:
        """
        Load lexicon data from the artifact bundled with the library.
        """
        pkg = importlib.resources.files("limes.data.de")
        lexicon_file = pkg.joinpath("lexicon.marisa")
        with importlib.resources.as_file(lexicon_file) as file:
            # We format the counts into little-Endian unsigned longs. This is
            # dictated by how the actual artifact was compiled;
            # see `scripts/compile_lexicon.py`.
            format = "<L"
            trie = RecordTrie(format)
            trie.load(file)
        return trie
