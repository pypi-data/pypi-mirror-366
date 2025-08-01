# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Barrier templates for supported Barriers."""

from enum import Enum

from limes.models import Barrier, BarrierCategorization


class GermanBarrierCategory(BarrierCategorization):
    """The category to which a barrier belongs."""

    HIGH_LANGUAGE_LEVEL = "Hohes sprachliches Niveau"
    COMPLEX_VERB_CONSTRUCT = "Komplexe Verb-Konstruktion"
    NEGATION = "Verneinung"
    SENTENCE_STRUCTURE = "Satzbau"
    INFORMATION_STRUCTURE = "Informationsstruktur"
    COMPOUNDS = "Komposita"
    WORD_CHOICE = "Wortwahl"


class GermanBarrier(Enum):
    # Category: High Language Level
    FOREIGN_PHRASE = Barrier(
        title="Fremdwort(-phrase)",
        category=GermanBarrierCategory.HIGH_LANGUAGE_LEVEL,
        description=(
            "Ein Lehnwort, das aus anderen Sprachen übernommen wurde aber noch "
            "so unangepasst sind, dass es als fremd empfunden wird."
        ),
        suggested_improvement="Ein anderes Wort mit gleicher Bedeutung finden.",
    )
    EDUCATIONAL_LANGUAGE = Barrier(
        title="Bildungssprachlicher Ausdruck",
        category=GermanBarrierCategory.HIGH_LANGUAGE_LEVEL,
        description=(
            "Eins oder mehrere Wörter, die in der gegebenen Form selten in der "
            "Alltagssprache vorkommen."
        ),
        suggested_improvement=(
            "Ein anderes Wort bzw. einen anderen Ausdruck mit gleicher "
            "Bedeutung finden."
        ),
    )
    COMPOUND_ADJECTIVE = Barrier(
        title="Zusammengesetztes Adjektiv",
        category=GermanBarrierCategory.HIGH_LANGUAGE_LEVEL,
        description=(
            "Ein Adjektiv aus zwei Teilen, dessen Gesamtbedeutung basierend "
            "auf den Teilen erst ermittelt werden muss. Das belastet das "
            "Arbeitsgedächtnis."
        ),
        suggested_improvement=(
            "Die Einzelwörter des zusammengesetzten Adjektivs in eine "
            "Wortgruppe (z.B. zwei einzelne Wörter) oder einen Satz überführen."
        ),
    )
    ATTRIBUTE_NOUN = Barrier(
        title="Eigenschafts-Substantiv",
        category=GermanBarrierCategory.HIGH_LANGUAGE_LEVEL,
        description=(
            "Ein Substantiv, das eine Eigenschaft oder einen Vorgang "
            "bezeichnet."
        ),
        suggested_improvement=(
            "Sie stellen nicht immer eine Barriere dar, bei längeren "
            "Substantiven sollte man aber prüfen, ob eine Vereinfachung durch "
            "Rückführung auf das eigentliche Adjektiv möglich ist."
        ),
    )
    COLLOCATIONAL_VERB_CONSTRUCT = Barrier(
        title="Funktionsverbgefüge",
        category=GermanBarrierCategory.HIGH_LANGUAGE_LEVEL,
        description=(
            "Eine Phrase, bei der die Bedeutung vom Verb auf das Substantiv "
            "ausgelagert wurde und bei der das Verb nicht mit seiner "
            "alltäglichen Bedeutung verstanden werden darf."
        ),
        suggested_improvement=(
            "Die Phrase kann oft durch ein einfaches Verb ersetzt werden."
        ),
    )
    MODAL_PHRASE = Barrier(
        title="Ersatzausdruck für Modalverb",
        category=GermanBarrierCategory.HIGH_LANGUAGE_LEVEL,
        description=(
            "Ein Satzbaustein, der eine Modalität mit einer längeren Phrase "
            "ausgedrückt, obwohl ein einziges Wort besser verstanden wird."
        ),
        suggested_improvement=(
            "Ersetzen durch einfache Modalverben ('können', 'müssen', 'sollen',"
            " 'dürfen', 'mögen', 'möchten')."
        ),
    )
    # Category: Complex Verb Construct
    DECOMPOSED_VERB = Barrier(
        title="Unfestes Verb",
        category=GermanBarrierCategory.COMPLEX_VERB_CONSTRUCT,
        description=(
            "Ein Verb, das in zwei Teile aufgespaltet wurde. Der eine Teil ist "
            "ein Verb, das oft auch alleine verwendet werden kann und dann eine"
            " andere Bedeutung hat. Je mehr Wörter zwischen den zwei Teilen "
            "liegen, desto mehr wird das Arbeitsgedächtnis belastet."
        ),
        suggested_improvement=(
            "Unfestes Verb in einer Nebensatzkonstruktion zusammenführen oder "
            "mit einem anderen Verb ausdrücken."
        ),
    )
    PASSIVE_VOICE = Barrier(
        title="Passivstruktur",
        category=GermanBarrierCategory.COMPLEX_VERB_CONSTRUCT,
        description=(
            "Das Vollverb tritt in partizipierter Form mit einer konjugierten "
            "Form von 'werden' oder 'sein' auf. Je größer die Distanz zwischen "
            "den beiden Komponenten, desto negativer wirkt sich die "
            "Passiv-Struktur auf die Lesbarkeit des Textes aus."
        ),
        suggested_improvement=(
            "Handelnde Person einfügen oder zumindest ein 'man'."
        ),
    )
    # Category: Negation
    NEGATION_AFFIX = Barrier(
        title="Verneinung durch Vor- oder Nachsilbe",
        category=GermanBarrierCategory.NEGATION,
        description=(
            "Das Wort muss erst morphologisch in das eigentliche Morphem sowie "
            "das Verneinungs-Affix aufgebrochen werden, bevor die Bedeutung des"
            " Wortes verarbeitet werden kann."
        ),
        suggested_improvement=(
            "Verneinung als eigenes Wort darstellen (z.B. 'ohne Farbstoff' "
            "statt 'Farbstofffrei')."
        ),
    )
    DOUBLE_NEGATION = Barrier(
        title="Doppelte Verneinung",
        category=GermanBarrierCategory.NEGATION,
        description="Die Bedeutung des Wortstamms wird zwei Mal invertiert.",
        suggested_improvement=(
            "Umformen vom doppelten Negativ ins Positiv (z.B. 'mit Wasser' "
            "statt 'nicht ohne Wasser')."
        ),
    )
    # Category: Sentence Structure
    LONG_SENTENCE = Barrier(
        title="Langer Satz",
        category=GermanBarrierCategory.SENTENCE_STRUCTURE,
        description=(
            "Lange Sätze sind häufig schwieriger zu verstehen als kurze Sätze."
        ),
        suggested_improvement=(
            "Versuchen, maximal 15 Wörter (per DIN Norm 8281-1) pro Satz zu "
            "verwenden. Oft kann man lange Sätze auch in mehrere kurze Sätze "
            "zerlegen."
        ),
    )
