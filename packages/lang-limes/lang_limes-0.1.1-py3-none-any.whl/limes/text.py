# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Module for the Text class."""

import numpy as np

from limes.analyzers.base import BaseAnalyzer
from limes.models import Barrier, ComplexityAlgorithm
from limes.parsers.interfaces import Parser
from limes.protocols import SpanProtocol
from limes.sentence import Sentence


class Text:
    """
    A text that is broken down into individual `Sentence` objects on which
    analyses can be performed.
    This object uses caching to avoid performing expensive computations
    redundantly.
    """

    def __init__(
        self,
        raw: str,
        analyzer: BaseAnalyzer,
        parser: Parser,
    ):
        """
        Create a `Text` object.

        Parameters
        ----------
        raw : str
            The string to be used as the bases if the text.
        analyzer : BaseAnalyzer
            The `BaseAnalyzer` used to perform barrier detection. This object
            contains the barrier analysis and complexity analysis logic.
        parser : Parser
            The `Parser` to be used for parsing relevant morphosyntactic
            information of the text.
        """
        self._raw = raw
        self._analyzer = analyzer
        self._parser = parser
        self._sentences: list[Sentence] | None = None

    @property
    def sentences(self) -> list[Sentence]:
        """
        A list of `Sentence` objects contained in the provided text.
        """
        if self._sentences is None:
            processed = self._parser(self._raw)
            self._sentences = [
                Sentence(sent, self._analyzer) for sent in processed.sents
            ]
        return self._sentences

    def __str__(self) -> str:
        """Return the raw text of the Text object."""
        return self._raw

    def __iter__(self):
        """
        Iterate over all `Sentence`s contained in the given text. The applied
        sentencization logic to split the `Text` into `Sentence` objects is
        determined by the `Parser` with which this `Text` was initialized.
        """
        yield from self.sentences

    def __getitem__(self, i: int) -> Sentence:
        """
        Return the i-th `Sentence` in the given text. The applied sentencization
        logic to split the `Text` into `Sentence` objects is determined by the
        `Parser` with which this `Text` was initialized.
        """
        return self.sentences[i]

    def __len__(self) -> int:
        """
        The length of the provided `Text` as determined by the number of
        `Sentence`s it contains.
        """
        return len(self.sentences)

    @property
    def barriers(self) -> list[Barrier]:
        """
        All barriers contained in the `Text`, as detected by the `Analyzer`
        attached to this `Text`.
        """
        barriers = []
        for sent in self:
            barriers.extend(sent.barriers)
        return barriers

    @property
    def local_complexities(self) -> list[tuple[SpanProtocol, float]]:
        """
        A list of syntactically coherent phrases that constitute the given
        sentence, as well as their respective calculated syntactic complexities.
        You can sum the local complexities to get a sound heuristic for the
        complexity of the complete sentence.
        """
        complexities: list[tuple[SpanProtocol, float]] = []
        for sent in self:
            complexities.extend(sent.local_complexities)
        return complexities

    def average_complexity(
        self,
        heuristic: ComplexityAlgorithm = ComplexityAlgorithm.AGGREGATED_LOCAL,
    ) -> float:
        """
        The complexity of the `Text` as a whole.

        Parameters
        ----------
        heuristic : ComplexityAlgorithm
            Determines which heuristic to use to calculate the complexity.
        """
        complexities = [sent.global_complexity(heuristic) for sent in self]
        return float(np.mean(complexities))
