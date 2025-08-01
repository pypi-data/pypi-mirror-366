# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Module for German text Analyzer."""

from limes.analyzers.base import BaseAnalyzer
from limes.analyzers.de.barrier_analyzer import GermanBarrierAnalyzer
from limes.analyzers.de.barriers import GermanBarrier
from limes.analyzers.de.complexity_analyzer import GermanComplexityAnalyzer
from limes.analyzers.de.lexicon import GermanLexicon
from limes.models import Barrier


class GermanAnalyzer(BaseAnalyzer):
    """
    An `Analyzer` specific to the German language, containing a
    `BarrierAnalyzer` as well as a `ComplexityAnalyzer` implementation specific
    to German.
    """

    def __init__(self):
        self.barrier_analyzer = GermanBarrierAnalyzer(lexicon=GermanLexicon())
        self.complexity_analyzer = GermanComplexityAnalyzer()

    @property
    def supported_barriers(self) -> list[Barrier]:
        """
        A list of all types of barriers that this analyzer can detect.
        """
        return [barrier.value for barrier in GermanBarrier]
