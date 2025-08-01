# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Module for the Detector base class."""

from limes.analyzers.interfaces import (
    BarrierAnalyzer,
    ComplexityAnalyzer,
)
from limes.models import Barrier, ComplexityAlgorithm
from limes.protocols import DocumentProtocol, SpanProtocol


class BaseAnalyzer:
    """
    Language-agnostic Analyzer object. This analyzer utilizes the
    `BarrierAnalyzer` and `ComplexityAnalyzer` interfaces to provide access to
    relevant analysis logic.
    """

    def __init__(
        self,
        barrier_analyzer: BarrierAnalyzer,
        complexity_analyzer: ComplexityAnalyzer,
    ):
        """
        Create a BaseAnalyzer object.

        Parameters
        ----------
        barrier_analyzer : BarrierAnalyzer
            The `BarrierAnalyzer` to be used to perform barrier detection.
        complexity_analyzer : ComplexityAnalyzer
            The `ComplexityAnalyzer` to be used to calculate text complexities.
        """
        self.barrier_analyzer = barrier_analyzer
        self.complexity_analyzer = complexity_analyzer

    @property
    def supported_barriers(self) -> list[Barrier]:
        """
        A list of all types of barriers that this analyzer can detect.
        """
        return self.barrier_analyzer.supported_barriers

    def detect_barriers(self, sentence: DocumentProtocol) -> list[Barrier]:
        """
        Detect `Barrier` instances in the provided sentence.
        """
        return self.barrier_analyzer(sentence)

    def compute_global_complexity(
        self,
        sentence: DocumentProtocol,
        heuristic: ComplexityAlgorithm,
    ) -> float:
        """
        Calculate the complexity of the entire sentence.
        """
        return self.complexity_analyzer.get_global_complexity(
            sentence=sentence,
            heuristic=heuristic,
        )

    def compute_local_complexities(
        self,
        sentence: DocumentProtocol,
    ) -> list[tuple[SpanProtocol, float]]:
        """
        Calculate complexity of separate parts of the sentence.
        """
        return self.complexity_analyzer.get_local_complexities(sentence)
