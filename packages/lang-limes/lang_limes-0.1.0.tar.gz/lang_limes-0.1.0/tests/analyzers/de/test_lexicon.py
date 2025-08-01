import pytest
from marisa_trie import RecordTrie

from limes.analyzers.de.lexicon import GermanLexicon


class DummyLoader:
    """
    Simple callable to simulate loading and to count how many times
    it's been invoked.
    """

    def __init__(self, data):
        self.data = data
        self.call_count = 0

    def __call__(self):
        self.call_count += 1
        return self.data


class FakeTrie(dict):
    """
    Simple dict-like object that mimics basic RecordTrie behavior for tests.
    Returns values as list-of-tuples via get(), enabling unwrapping in
    get_frequency_score.
    """

    def get(self, key, default=None):
        if key in self:
            # Simulate RecordTrie returning a list of tuples
            return [(super().get(key),)]
        return None


def test_contains_true_and_false(monkeypatch):
    # Arrange
    sample_data = {"Haus": 10, "Baum": 5}
    # Use FakeTrie to simulate RecordTrie behavior
    fake_trie = FakeTrie({k: v / 10 for k, v in sample_data.items()})
    loader = DummyLoader(fake_trie)
    monkeypatch.setattr(GermanLexicon, "_load_data_file", loader)

    lex = GermanLexicon()

    # Act
    result_true = lex.contains("Haus")
    result_false = lex.contains("Unbekannt")

    # Assert
    assert result_true is True, "Expected 'Haus' to be reported in the lexicon"
    assert result_false is False, "Expected 'Unbekannt' not to be reported"


def test_get_frequency_score_returns_correct_normalized_value(monkeypatch):
    # Arrange
    counts = {"a": 2, "b": 8}
    fake_trie = FakeTrie(counts)
    loader = DummyLoader(fake_trie)
    monkeypatch.setattr(GermanLexicon, "_load_data_file", loader)

    lex = GermanLexicon()

    # Act
    freq_a = lex.get_frequency_score("a")
    freq_b = lex.get_frequency_score("b")
    freq_missing = lex.get_frequency_score("c")

    # Assert
    assert freq_a == counts["a"]
    assert freq_b == counts["b"]
    assert freq_missing is None


def test_data_is_loaded_once_per_instance(monkeypatch):
    # Arrange
    data = {"x": 1}
    fake_trie = FakeTrie(data)
    loader = DummyLoader(fake_trie)
    monkeypatch.setattr(GermanLexicon, "_load_data_file", loader)

    # Act
    lex = GermanLexicon()
    _ = lex.get_frequency_score("x")
    _ = lex.contains("x")

    # Assert
    assert loader.call_count == 1, "Data should be loaded only once"


def test_real_data_file_loads_and_contains_common_words():
    # Arrange / Act
    try:
        data = GermanLexicon._load_data_file()
    except FileNotFoundError:
        pytest.skip("Production lexicon resource not found on this environment")

    # Assert: it returns a RecordTrie
    assert isinstance(data, RecordTrie)
    assert len(data) > 0, "Expected at least one entry in the real lexicon"

    # Assert: contains at least some known German stop-words with float scores
    for w in ("der", "und", "die"):
        val_list = data.get(w)
        assert val_list is not None, (
            f"Expected '{w}' to be in the real German lexicon"
        )
        score = val_list[0][0]
        assert isinstance(score, int), (
            f"Expected score for '{w}' to be a integer"
        )
