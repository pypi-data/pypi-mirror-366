# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
import inspect
from abc import ABC, abstractmethod

from limes.models import Barrier, ComplexityAlgorithm
from limes.protocols import DocumentProtocol, SpanProtocol


class BarrierAnalyzer(ABC):
    """
    Class for identifying language barriers.
    """

    def __call__(self, sentence: DocumentProtocol) -> list[Barrier]:
        """
        Automatically identify and run all public detection functions of the
        Analyzer. Overwrite this with concrete registration of all relevant
        callables for minor overhead reduction.
        """
        # Get all methods of the class that match the required signature.
        methods = self._get_methods_with_signature()
        if len(methods) == 0:
            raise AttributeError(
                "The class did not identify any detection functions to be used."
            )

        barriers = []
        for method in methods:
            barriers.extend(method(sentence))
        return barriers

    def _get_methods_with_signature(self):
        """
        Identify functions contained in the given class that follow the detector
        function format.
        """
        # Get all methods of the class.
        methods = inspect.getmembers(self, predicate=inspect.ismethod)

        # Filter methods that match barrier detection function signature.
        filtered_methods = []
        for name, method in methods:
            # Only evaluate classes that have a name that indicates relevance.
            if not name.startswith("detect"):
                continue
            sig = inspect.signature(method)
            # Skip methods where the function parameters don't match.
            if not len(sig.parameters) == 1 or "sentence" not in sig.parameters:
                continue
            # Skip methods where return type does not match.
            return_type = sig.return_annotation
            if not return_type == list[Barrier]:
                continue

            filtered_methods.append(method)
        return filtered_methods

    @property
    @abstractmethod
    def supported_barriers(self) -> list[Barrier]:
        """
        A list of all types of barriers that this analyzer can detect.
        """
        ...


class ComplexityAnalyzer(ABC):
    """
    Class for calculating language complexity.
    """

    @abstractmethod
    def get_global_complexity(
        self,
        sentence: DocumentProtocol,
        heuristic: ComplexityAlgorithm,
    ) -> float:
        """
        Calculate the complexity of the entire sentence.

        Parameters
        ----------
        sentence : DocumentProtocol
            The sentence for which the complexity is to be calculated. Please
            note that this function is designed to perform only on single
            sentences but won't complain if you pass a DocumentProtocol instance
            that constitutes a complete text. In that case, the values returned
            may be nonsensical.
        heuristic : ComplexityAlgorithm
            Determines which heuristic to use to calculate the complexity.
        """
        ...

    @abstractmethod
    def get_local_complexities(
        self,
        sentence: DocumentProtocol,
    ) -> list[tuple[SpanProtocol, float]]:
        """
        Get a list of syntactically coherent phrases that constitute the given
        text, as well as their respective calculated syntactic complexities.
        You can sum the local complexities to get a sound heuristic for the
        complexity of the complete sentence.
        """
        ...


class Lexicon(ABC):
    """
    Class for retrieving information regarding word frequency and lexicon
    membership. Concrete implementations might also serve as interfaces for
    language-specific lexical resources such as word groups and affixes.

    Lexicons require instantiation because resources for them are loaded lazily
    but remain in memory because it is likely that the same kind of lookup will
    be performed multiple times over the lifetime of a Lexicon instance.
    """

    @abstractmethod
    def contains(self, word: str) -> bool:
        """Check whether the given word is contained in the lexicon."""
        ...

    @abstractmethod
    def get_frequency(self, word: str) -> int | None:
        """
        Identify how frequent a given word is in the given Lexicon. Please note
        that frequency is described in relative terms, normalized to [0.0, 1.0].
        """
        ...
