"""Integration tests for the String Container objects."""

import pytest
import spacy

from limes import Barrier, GermanAnalyzer, Text
from limes.analyzers.de.complexity_analyzer import GermanComplexityAnalyzer
from limes.models import ComplexityAlgorithm
from limes.parsers.spacy_parser import SpacyParser, SpacySpanAdapter
from limes.sentence import Sentence


@pytest.fixture(scope="session")
def parser() -> SpacyParser:
    """The SpacyParser to be used as foundation for the parsing logic."""
    nlp = spacy.load("de_core_news_sm")
    nlp.add_pipe("sentencizer")
    return SpacyParser(nlp)


@pytest.fixture(scope="session")
def analyzer() -> GermanAnalyzer:
    """The analyzer to be used for analysis."""
    return GermanAnalyzer()


@pytest.fixture(scope="function")
def text(parser: SpacyParser, analyzer: GermanAnalyzer) -> Text:
    """A reference string container."""
    return Text(
        "Das hier ist ein Text. Er hat zwei Sätze.",
        analyzer=analyzer,
        parser=parser,
    )


class TestText:
    """Test cases around the `Text` string container integration."""

    def test_parsing(self, text: Text):
        # Test iteration.
        assert text._sentences is None
        for sent in text:
            assert isinstance(sent, Sentence)
        assert isinstance(text._sentences, list) and len(text._sentences) == 2

    def test_average_complexity(self, text: Text):
        complexity = text.average_complexity()
        assert isinstance(complexity, float)
        assert complexity >= 0.0

    def test_barriers(self, text: Text):
        barriers = text.barriers
        assert isinstance(barriers, list)
        for element in barriers:
            assert isinstance(element, Barrier)


class TestComplexityAnalyzer:
    """
    Test cases around complexity analysis functionality in the string container
    classes.
    """

    def test_global_complexity(self, text: Text):
        complexity_analyzer = GermanComplexityAnalyzer()
        # Make sure cache is empty.
        cache_key = text[0]._sent.text
        assert cache_key not in complexity_analyzer._global_complexity_cache
        complexity = complexity_analyzer.get_global_complexity(
            text[0]._sent,
            heuristic=ComplexityAlgorithm.GLOBAL,
        )
        assert isinstance(complexity, float)
        assert complexity >= 0.0
        assert cache_key in complexity_analyzer._global_complexity_cache
        # Manually overwrite the value to double_check that cache value is
        # retrieved rather than recalculated.
        dummy_value = complexity * 1.75
        complexity_analyzer._global_complexity_cache[cache_key] = dummy_value
        assert (
            complexity_analyzer.get_global_complexity(
                text[0]._sent,
                heuristic=ComplexityAlgorithm.GLOBAL,
            )
            == dummy_value
        )

    def test_global_aggregate_complexity(self, text: Text):
        complexity_analyzer = GermanComplexityAnalyzer()
        cache_key = text[0]._sent.text
        assert cache_key not in complexity_analyzer._local_complexities_cache
        complexity = complexity_analyzer.get_global_complexity(
            text[0]._sent,
            heuristic=ComplexityAlgorithm.AGGREGATED_LOCAL,
        )
        assert isinstance(complexity, float)
        assert complexity >= 0.0
        assert cache_key in complexity_analyzer._local_complexities_cache
        # Manually overwrite the value to double_check that cache value is
        # retrieved rather than recalculated.
        dummy_complexity = complexity * 1.75
        dummy_span = text[0]._sent.span(0, 2)
        complexity_analyzer._local_complexities_cache[cache_key] = [
            (dummy_span, dummy_complexity),
            (dummy_span, dummy_complexity),
        ]
        assert (
            complexity_analyzer.get_global_complexity(
                text[0]._sent,
                heuristic=ComplexityAlgorithm.AGGREGATED_LOCAL,
            )
            == dummy_complexity * 2  # *2 because we added two separate spans.
        )

    def test_calculate_local_complexities(self, text: Text):
        complexity_analyzer = GermanComplexityAnalyzer()
        cache_key = text[0]._sent.text
        assert cache_key not in complexity_analyzer._local_complexities_cache

        # Test Calculation.
        complexities = complexity_analyzer.get_local_complexities(text[0]._sent)

        # Ensure results are in cache.
        assert cache_key in complexity_analyzer._local_complexities_cache

        assert len(complexities) > 0
        for i, result in enumerate(complexities):
            assert len(result) == 2
            assert isinstance(result[0], SpacySpanAdapter)
            assert isinstance(result[1], float)
            assert result[1] >= 0

            # Alter value in cache to see if cache is used for retrieval.
            complexity_analyzer._local_complexities_cache[cache_key][i] = (
                result[0],
                -1.0,
            )

        # Test retrieval from cache.
        other_complexities = complexity_analyzer.get_local_complexities(
            text[0]._sent,
        )
        for new_result in other_complexities:
            assert new_result[1] == -1.0
