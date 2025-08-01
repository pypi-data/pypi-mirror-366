"""
Tests for the ComplexityAnalyzer class. Please note that these tests are unclean
in the sense that they do not properly mock external dependencies such as the
parsed sentence. This is a trade-off to limit test-writing complexity which
would be enourmous for the complex cases that are being modelled in the class to
be tested.
"""

import pytest
import spacy

from limes.analyzers.de.complexity_analyzer import GermanComplexityAnalyzer
from limes.models import ComplexityAlgorithm
from limes.parsers.spacy_parser import SpacyParser
from limes.protocols import DocumentProtocol, SpanProtocol


@pytest.fixture(scope="module")
def spacy_pipeline() -> spacy.language.Language:
    return spacy.load("de_core_news_sm")


@pytest.fixture(scope="module")
def parser(spacy_pipeline: spacy.language.Language) -> SpacyParser:
    """
    A parser to be used to create objects to test on.
    """
    return SpacyParser(spacy_pipeline)


@pytest.fixture(scope="module")
def sentence_with_verb(parser: SpacyParser) -> DocumentProtocol:
    """
    A parsed sentence that contains a verb.
    """
    return parser("Ich mag Züge.")


@pytest.fixture(scope="module")
def sentence_without_verb(parser: SpacyParser) -> DocumentProtocol:
    """
    A parsed sentence that contains a verb.
    """
    return parser("Ein Satz.")


@pytest.fixture(scope="module")
def complexity_analyzer() -> GermanComplexityAnalyzer:
    """
    Instance of GermanComplexityAnalyzer for each test.
    """
    analyzer = GermanComplexityAnalyzer()
    return analyzer


class TestGlobalComplexities:
    """
    Test cases for functionality around global complexity.
    """

    @pytest.mark.parametrize(
        "algorithm",
        [ComplexityAlgorithm.GLOBAL, ComplexityAlgorithm.AGGREGATED_LOCAL],
    )
    def test_successful_execution(
        self,
        complexity_analyzer: GermanComplexityAnalyzer,
        sentence_with_verb: DocumentProtocol,
        algorithm: ComplexityAlgorithm,
    ):
        complexity = complexity_analyzer.get_global_complexity(
            sentence=sentence_with_verb,
            heuristic=algorithm,
        )

        assert isinstance(complexity, float)
        assert complexity > 0


class TestLocalComplexity:
    """Test cases for functionality around local complexity."""

    def test_successful_execution(
        self,
        complexity_analyzer: GermanComplexityAnalyzer,
        sentence_with_verb: DocumentProtocol,
    ):
        complexities = complexity_analyzer.get_local_complexities(
            sentence=sentence_with_verb,
        )

        assert isinstance(complexities, list)
        for complexity in complexities:
            assert isinstance(complexity, tuple) and len(complexity) == 2
            assert isinstance(complexity[0], SpanProtocol)
            assert isinstance(complexity[1], float) and complexity[1] >= 0.0
