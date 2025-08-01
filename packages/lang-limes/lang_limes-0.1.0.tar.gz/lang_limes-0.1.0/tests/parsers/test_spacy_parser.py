"""Test cases around the SpacyParser and related adapters."""

import pytest
import spacy

from limes.parsers.spacy_parser import (
    SpacyDocumentAdapter,
    SpacyParser,
    SpacySpanAdapter,
    SpacyTokenAdapter,
)


@pytest.fixture(scope="module")
def spacy_model_name() -> str:
    return "de_core_news_sm"


@pytest.fixture(scope="module")
def spacy_pipeline(spacy_model_name: str) -> spacy.language.Language:
    return spacy.load(spacy_model_name)


@pytest.fixture(scope="module")
def parser(spacy_pipeline: spacy.language.Language) -> SpacyParser:
    return SpacyParser(spacy_pipeline)


class TestSpacyParser:
    """Test class for SpacyParser tests."""

    def test_init_from_string(self, spacy_model_name):
        # Arrange & Act
        parser = SpacyParser(spacy_model_name)
        # Assert
        assert isinstance(parser._nlp, spacy.language.Language)

    def test_init_from_spacy_pipeline(
        self,
        spacy_pipeline: spacy.language.Language,
    ):
        # Arrange & Act
        parser = SpacyParser(spacy_pipeline)
        # Assert
        assert isinstance(parser._nlp, spacy.language.Language)

    def test_call_method(self, parser):
        # Arrange
        text = "Dies ist ein Testtext."
        # Act
        doc = parser(text)
        # Assert
        assert isinstance(doc, SpacyDocumentAdapter)
        assert doc.text == text


# Test class for the SpacyTokenAdapter functionality
class TestSpacyTokenAdapter:
    @pytest.fixture(scope="class")
    def token_adapter(
        self,
        spacy_pipeline: spacy.language.Language,
    ) -> SpacyTokenAdapter:
        doc = spacy_pipeline("Dies ist ein Testtext.")
        return SpacyTokenAdapter(doc[0])

    def test_properties(self, token_adapter: SpacyTokenAdapter):
        assert isinstance(token_adapter.text, str)
        assert isinstance(token_adapter.morph, dict)
        assert isinstance(token_adapter.pos_, str)
        assert isinstance(token_adapter.fine_pos, str)
        assert isinstance(token_adapter.dep_, str)
        assert isinstance(token_adapter.lemma_, str)
        assert isinstance(token_adapter.i, int)
        assert isinstance(token_adapter.head, SpacyTokenAdapter)
        assert isinstance(token_adapter.is_punct, bool)
        assert isinstance(list(token_adapter.children), list)
        assert isinstance(list(token_adapter.ancestors), list)
        assert isinstance(list(token_adapter.subtree), list)


class TestSpacySpanAdapter:
    """Test class for SpacySpanAdapter functionality."""

    @pytest.fixture
    def span_adapter(
        self,
        spacy_pipeline: spacy.language.Language,
    ) -> SpacySpanAdapter:
        doc = spacy_pipeline("Dies ist ein Testtext.")
        return SpacySpanAdapter(doc[0:3])

    def test_properties(self, span_adapter: SpacySpanAdapter):
        # Assert
        assert isinstance(span_adapter.text, str)
        assert isinstance(list(span_adapter.noun_chunks), list)

    def test_iteration(self, span_adapter: SpacySpanAdapter):
        # Arrange & Act
        tokens = [token for token in span_adapter]
        # Assert
        assert all(isinstance(tok, SpacyTokenAdapter) for tok in tokens)


class TestSpacyDocumentAdapter:
    """Test class for SpacyDocumentAdapter functionality."""

    @pytest.fixture
    def doc_adapter(
        self,
        spacy_pipeline: spacy.language.Language,
    ) -> SpacyDocumentAdapter:
        text = "Dies ist ein Testtext."
        return SpacyDocumentAdapter(spacy_pipeline(text))

    def test_properties(self, doc_adapter: SpacyDocumentAdapter):
        assert isinstance(doc_adapter.text, str)
        assert isinstance(list(doc_adapter.noun_chunks), list)
        assert len(doc_adapter) > 0

    def test_iteration(self, doc_adapter: SpacyDocumentAdapter):
        # Arrange & Act
        tokens = [token for token in doc_adapter]
        # Assert
        assert all(isinstance(tok, SpacyTokenAdapter) for tok in tokens)
