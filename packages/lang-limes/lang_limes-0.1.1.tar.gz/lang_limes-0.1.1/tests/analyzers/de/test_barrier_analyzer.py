"""
Tests for the German-specific implementation of the BarrierAnalyzer. Please note
that this test suite has an unfortunate dependency on the SpacyParser component
as it saves time mocking the complex subjects we're operating on.
"""

import pytest

from limes.analyzers.de.barrier_analyzer import GermanBarrierAnalyzer
from limes.analyzers.de.lexicon import GermanLexicon
from limes.models import Barrier
from limes.parsers.spacy_parser import SpacyParser


@pytest.fixture(scope="module")
def parser() -> SpacyParser:
    """
    Please note that these tests require accurate parsing, therefore a much
    larger model is needed for testing.
    """
    return SpacyParser("de_dep_news_trf")


@pytest.fixture(scope="module")
def barrier_analyzer() -> GermanBarrierAnalyzer:
    return GermanBarrierAnalyzer(
        lexicon=GermanLexicon(),
    )


def evaluate_results(barriers: list[Barrier], true_positives: list[list[str]]):
    """
    Helper function because most test cases have the same way of asserting
    correctness.
    """
    assert len(barriers) == len(true_positives)
    if len(barriers) > 0:
        for result, truth in zip(barriers, true_positives):
            assert result.affected_tokens, (
                "Detected barriers should contain examples."
            )
            assert len(result.affected_tokens) == len(truth)
            for i, token in enumerate(result.affected_tokens):
                assert token.text == truth[i]


def test_supported_barriers(barrier_analyzer: GermanBarrierAnalyzer):
    barriers = barrier_analyzer.supported_barriers
    assert len(barriers) > 0
    for entry in barriers:
        assert isinstance(entry, Barrier), (
            "All entries should be `Barrier` instances."
        )
        assert entry.title != "", "Barrier is missing a title!"
        assert entry.description != "", "Barrier is missing a description!"
        assert entry.suggested_improvement != "", (
            "Barrier is missing a suggested improvement!"
        )
        assert entry.affected_tokens is None, (
            "General barriers should not have tokens attached to it!"
        )


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "phrases"),
    (
        (
            "Software-Tests sind eine abstrakte Sache.",
            [["abstrakte"]],
        ),
        (
            "Mein modus operandi ist, mir irgendwas aus den Fingern zu saugen.",
            [["modus", "operandi"]],
        ),
        (
            "Mein Mathe-Lehrer sagte, dass man Beweise mit quod erat demonstrandum abschließt.",
            [["quod", "erat", "demonstrandum"]],
        ),
        (
            "Ich bin Atheist und vulgär.",
            [["Atheist"], ["vulgär"]],
        ),
        # For some tokens, spacy generates no lemmas ("de" and "facto" both falling in that
        # category). Test the token-fallback in this case.
        (
            "Hier verwenden wir de facto auch noch eine Fremdsprachen-Phrase.",
            [["de", "facto"]],
        ),
    ),
)
def test_detect_foreign_phrases(
    parser: SpacyParser,
    barrier_analyzer: GermanBarrierAnalyzer,
    sentence: str,
    phrases: list[list[str]],
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_foreign_phrases(doc)
    evaluate_results(results, phrases)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "educational_language_verbs"),
    (
        (
            "Ich habe die Optionen erkundet und für gut befunden.",
            [["erkundet"], ["befunden"]],
        ),
        (
            "Das Gerät entzieht der Raumluft Feuchtigkeit",
            [["entzieht"]],
        ),
        (
            "Die Fertigung ist von mangelhafter Qualität.",
            [["mangelhafter"]],
        ),
        (
            "Das ist gängige Praxis und vom Prozessablauf einwandfrei.",
            [["gängige"], ["einwandfrei"]],
        ),
        (
            "Anschließend muss man das Auto abschließen.",
            [["Anschließend"]],
        ),
        (
            "Das ist überwiegend dem Chef geschuldet und demzufolge sehr frustrierend.",
            [["überwiegend"], ["demzufolge"]],
        ),
    ),
)
def test_detect_educational_language_words(
    barrier_analyzer: GermanBarrierAnalyzer,
    parser: SpacyParser,
    sentence: str,
    educational_language_verbs: list[list[str]],
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_educational_language_words(doc)
    evaluate_results(results, educational_language_verbs)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "compounds"),
    (
        (
            "Die Abbildung von Vektorgrafiken erfolgt im Gegensatz dazu auflösungsunabhängig.",
            [["auflösungsunabhängig"]],
        ),
        (
            "CMYK-Farbräume sind immer geräte- und prozessabhängig.",
            [["prozessabhängig"]],
        ),
        (
            "Die richtigen Rasterpunkte sind größenvariabel aber nicht anderweitig variabel.",
            [["größenvariabel"]],
        ),
        (
            "Das salzhaltige Gebäck ist hitzebeständig und kritikresistent.",
            [["salzhaltige"], ["hitzebeständig"], ["kritikresistent"]],
        ),
    ),
)
def test_detect_compound_adjective(
    barrier_analyzer: GermanBarrierAnalyzer,
    parser: SpacyParser,
    sentence: str,
    compounds: list[list[str]],
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_compound_adjective(doc)
    evaluate_results(results, compounds)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "attribute_nouns"),
    (
        (
            "Die allen Sperrgetrieben gemeinsame Eigenschaft ist die Unstetigkeit der Bewegung.",
            [["Unstetigkeit"]],
        ),
        (
            "Dann evaluieren wir die Lösung noch hingehend ihrer Säurefreiheit und Klebefähigkeit.",
            [["Säurefreiheit"], ["Klebefähigkeit"]],
        ),
        (
            "Die richtigen Rasterpunkte sind größenvariabel aber nicht anderweitig variabel.",
            [],
        ),
    ),
)
def test_detect_attribute_nouns(
    barrier_analyzer: GermanBarrierAnalyzer,
    parser: SpacyParser,
    sentence: str,
    attribute_nouns: list[list[str]],
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_attribute_nouns(doc)
    evaluate_results(results, attribute_nouns)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "constructs"),
    (
        (
            "Verwendet man Wechselspannung, kommen Wechselstromwiderstände in Betracht.",
            [["kommen", "in", "Betracht"]],
        ),
        (
            "Damit das Druckwerk zum Stillstand gebracht werden kann, befinden sich an den Enden "
            "der Tragarme pneumatisch betätigte Scheibenbremsen aus Stahl.",
            [["zum", "Stillstand", "gebracht"]],
        ),
        (
            "Büttenpapiere stehen nur noch im handwerklich-künstlerischen Bereich zur Verfügung.",
            [["stehen", "zur", "Verfügung"]],
        ),
    ),
)
def detect_collocational_verb_construct(
    barrier_analyzer: GermanBarrierAnalyzer,
    parser: SpacyParser,
    sentence: str,
    constructs: list[list[str]],
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_collocational_verb_construct(doc)
    evaluate_results(results, constructs)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "modal_verb_constructs"),
    (
        (
            "Die Werte sind zu bestimmen.",
            [["sind", "zu", "bestimmen"]],
        ),
        (
            "Zuerst hat X die Werte zu bestimmen.",
            [["hat", "zu", "bestimmen"]],
        ),
        (
            "Zuerst hat X die Werte abzugeben.",
            [["hat", "abzugeben"]],
        ),
        (
            "Die Werte lassen sich bestimmen.",
            [["lassen", "sich", "bestimmen"]],
        ),
        (
            "X erlaubt es, die Werte zu bestimmen.",
            [["erlaubt", "es", "zu", "bestimmen"]],
        ),
        (
            "X erlaubt es, die Werte abzugeben.",
            [["erlaubt", "es", "abzugeben"]],
        ),
        (
            "Diese Dinge kommen als Sensoren in Betracht",
            [["kommen", "in", "Betracht"]],
        ),
        (
            "Bauern sind in der Lage, den Straßenverkehr lahmzulegen und sie sind auch in der "
            "Lage, meinen Alltag zu stören.",
            [
                ["in", "der", "Lage", "lahmzulegen"],
                ["in", "der", "Lage", "zu", "stören"],
            ],
        ),
    ),
)
def test_detect_substitute_expression_for_modality(
    barrier_analyzer: GermanBarrierAnalyzer,
    parser: SpacyParser,
    sentence: str,
    modal_verb_constructs: list[list[str]],
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_substitute_expression_for_modality(doc)
    evaluate_results(results, modal_verb_constructs)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "decomposed_verbs"),
    [
        (
            "Ich kaufe Schuhe.",
            [],
        ),
        (
            "Ich kaufe ein.",
            [("kaufe", "ein")],
        ),
        (
            "Dazu fällt mir nichts mehr ein, wirklich.",
            [("fällt", "ein")],
        ),
        (
            "Dazu ist mir nichts mehr eingefallen, wirklich.",
            [],
        ),
        (
            "Ich esse das ganz sicher nicht auf, das ist voll ekelhaft.",
            [("esse", "auf")],
        ),
        (
            "Ich werde das ganz sicher nicht aufessen, das ist voll ekelhaft.",
            [],
        ),
        (
            "Ich esse noch kurz auf und dann kaufe ich ein und trage dich in den Plan ein, okay?",
            [("esse", "auf"), ("kaufe", "ein"), ("trage", "ein")],
        ),
    ],
)
def test_detect_decomposed_verbs(
    barrier_analyzer: GermanBarrierAnalyzer,
    parser: SpacyParser,
    sentence: str,
    decomposed_verbs: list[list[str]],
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_decomposed_verbs(doc)
    evaluate_results(results, decomposed_verbs)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "passive_components"),
    [
        # Simple clause without passive.
        ("Sie feiern den Geburtstag", []),
        # Simple clause with passive.
        ("Der Geburtstag wurde von ihnen gefeiert.", [("wurde", "gefeiert")]),
        # Main clause without passive, subclause without passive.
        ("Sie feierten Geburtstag, weshalb sie Kuchen aßen.", []),
        # Main clause with passive, subclause without passive.
        (
            "Der Geburtstag wurde gefeiert, weshalb sie Kuchen aßen.",
            [("wurde", "gefeiert")],
        ),
        # Main clause without passive, subclause with passive.
        (
            "Sie feierten Geburtstag, weshalb Kuchen gegessen wurde.",
            [("wurde", "gegessen")],
        ),
        # Main clause with passive, subclause with passive.
        (
            "Der Geburtstag wurde gefeiert, weshalb Kuchen gegessen wurde.",
            [("wurde", "gefeiert"), ("wurde", "gegessen")],
        ),
        # Main clause without passive, multiple subclauses with multiple passives.
        (
            (
                "Ich esse den Kuchen, der grün angemalt wurde, "
                "was ich doof finde und mir nicht zur Wahl gestellt wurde."
            ),
            [("wurde", "angemalt"), ("wurde", "gestellt")],
        ),
    ],
)
def test_detect_passive_voice(
    barrier_analyzer: GermanBarrierAnalyzer,
    parser: SpacyParser,
    sentence: str,
    passive_components: list[list[str]],
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_passive_voice(doc)
    evaluate_results(results, passive_components)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "negations"),
    (
        (
            "Ich gehe atemlos durch die Nacht.",
            [["atemlos"]],
        ),
        # Ensure words equal to a negation suffix (e.g. "los") aren't matched.
        (
            "Wenn du konservierungsstofffreie Lebensmittel zu dir nimmst, ist was los.",
            [["konservierungsstofffreie"]],
        ),
        (
            "Der Kunde war wirklich unfreundlich und generell desinteressiert.",
            [["unfreundlich"], ["desinteressiert"]],
        ),
        # Ensure that substantivized instances don't get matched.
        (
            "Illoyalität ist nicht cool.",
            [],
        ),
        (
            "Es ist nicht cool, wenn du illoyal bist.",
            [["illoyal"]],
        ),
        # Ensure that double negatives are detected.
        (
            "Es ist nicht ungewollt, wenn du illoyal bist.",
            [["nicht", "ungewollt"], ["illoyal"]],
        ),
    ),
)
def test_detect_negation(
    barrier_analyzer: GermanBarrierAnalyzer,
    parser: SpacyParser,
    sentence: str,
    negations: list[list[str]],
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_negation(doc)
    assert len(results) == len(negations)
    for orig, result in zip(negations, results):
        assert result.affected_tokens is not None
        if len(result.affected_tokens) > 1:
            assert result.title == "Doppelte Verneinung"
        else:
            assert result.title == "Verneinung durch Vor- oder Nachsilbe"
        for i, token in enumerate(result.affected_tokens):
            assert orig[i] == str(token)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("sentence", "is_too_long"),
    [
        (
            "Wir beobachten eine Abnahme der Dehnbarkeit.",
            False,
        ),
        (
            "Wir beobachten, auch mit Satzzeichen, eine Abnahme der Dehnbarkeit...",
            False,
        ),
        (
            "Dieser Satz ist gerade an der Grenze dazu, zu lang zu sein.",
            False,
        ),
        (
            "Wir haben uns heute hier versammelt, um uns unnötig lange Sätze auszudenken, die "
            "länger als 13 Wörter sind.",
            True,
        ),
    ],
)
def test_detect_long_sentence(
    barrier_analyzer: GermanBarrierAnalyzer,
    parser: SpacyParser,
    sentence,
    is_too_long,
):
    doc = parser(sentence)
    results = barrier_analyzer.detect_long_sentence(doc)
    assert (len(results) == 1) == is_too_long
