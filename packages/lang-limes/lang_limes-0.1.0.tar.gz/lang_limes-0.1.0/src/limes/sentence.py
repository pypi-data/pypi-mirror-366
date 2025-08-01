# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Module for the Sentence class."""

from limes.analyzers.base import BaseAnalyzer
from limes.models import Barrier, ComplexityAlgorithm
from limes.protocols import DocumentProtocol, SpanProtocol


class Sentence:
    """
    A sentence that is broken down into its individual constituents and their
    associated metadata.
    This object utilizes caching to avoid performing expensive computations
    redundantly.
    """

    def __init__(self, sent: DocumentProtocol, analyzer: BaseAnalyzer):
        """
        Create a `Sentence` object.

        Parameters
        ----------
        sent : DocumentProtocol
            A sentence, as parsed by a `Parser` object.
        analyzer : Analyzer
            The analyzer that is to be used for actual barrier analysis.
        """
        self._sent = sent
        self._analyzer = analyzer
        # Cache variables.
        self._barriers: list[Barrier] | None = None
        self._local_complexities: list[tuple[SpanProtocol, float]] | None = None

    def __str__(self) -> str:
        """Return the raw string of the sentence."""
        return str(self._sent)

    @property
    def barriers(self) -> list[Barrier]:
        """
        All barriers contained in the sentence, as detected by the `Analyzer`
        attached to this sentence.
        """
        if self._barriers is None:
            self._barriers = self._analyzer.detect_barriers(self._sent)
        return self._barriers

    @property
    def local_complexities(self) -> list[tuple[SpanProtocol, float]]:
        """
        A list of syntactically coherent phrases that constitute the given
        sentence, as well as their respective calculated syntactic complexities.
        You can sum the local complexities to get a sound heuristic for the
        complexity of the complete sentence.
        """
        if self._local_complexities is None:
            self._local_complexities = (
                self._analyzer.compute_local_complexities(self._sent)
            )
        return self._local_complexities

    def global_complexity(
        self,
        heuristic: ComplexityAlgorithm = ComplexityAlgorithm.AGGREGATED_LOCAL,
    ) -> float:
        """
        The complexity of the sentence as a whole.

        Parameters
        ----------
        heuristic : ComplexityAlgorithm
            Determines which heuristic to use to calculate the complexity.
        """
        return self._analyzer.compute_global_complexity(self._sent, heuristic)
