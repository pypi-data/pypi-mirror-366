# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
import numpy as np

from limes.analyzers.interfaces import ComplexityAnalyzer
from limes.analyzers.mixins import SyntaxAnalyzerMixin
from limes.models import ComplexityAlgorithm
from limes.protocols import DocumentProtocol, SpanProtocol


class GermanComplexityAnalyzer(ComplexityAnalyzer, SyntaxAnalyzerMixin):
    """A `ComplexityAnalyzer` that is specific to the German language."""

    def __init__(self):
        self._local_complexities_cache: dict[
            str,
            list[tuple[SpanProtocol, float]],
        ] = {}
        self._global_complexity_cache: dict[str, float] = {}

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

        Raises
        ------
        NoRootVerbError: If no root can be found in the given sentence.
        """
        if heuristic == ComplexityAlgorithm.AGGREGATED_LOCAL:
            return sum(
                component[1]
                for component in self.get_local_complexities(
                    sentence,
                )
            )
        if sentence.text in self._global_complexity_cache:
            return self._global_complexity_cache[sentence.text]
        complexity = self._compute_global_complexity(sentence)
        self._global_complexity_cache[sentence.text] = complexity
        return complexity

    def _compute_global_complexity(self, sentence: DocumentProtocol) -> float:
        """
        Actually perform the computations to identify the global complexity
        value of the provided sentence.
        """
        dependency_stats = self.evaluate_syntax(sentence)
        backwards_dependency = (
            dependency_stats.backwards_dependencies_count
            * dependency_stats.mean_backwards_dependency_length
        )
        forward_dependency = (
            dependency_stats.forward_dependencies_count
            * dependency_stats.mean_forward_dependency_length
        )
        core_root = (
            dependency_stats.max_children
            * dependency_stats.biggest_root_relative_position
        )
        complexity = backwards_dependency * 2 + forward_dependency + core_root
        return complexity

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
        if sentence.text in self._local_complexities_cache:
            return self._local_complexities_cache[sentence.text]
        local_complexities = self._compute_local_complexities(sentence)
        self._local_complexities_cache[sentence.text] = local_complexities
        return local_complexities

    def _compute_local_complexities(
        self,
        sentence: DocumentProtocol,
    ) -> list[tuple[SpanProtocol, float]]:
        """
        Calculate the local complexity of each verb phrase in a given sentence.
        """
        scores: list[tuple[SpanProtocol, float]] = []
        verb_phrases = self.identify_verb_phrases(sentence)
        for verb_idx, phrase in verb_phrases.items():
            try:
                phrase_span = self.phrase_idx_to_span(sentence, phrase)
            except IndexError:
                continue
            phrase_difficulty = self.calculate_verb_phrase_complexity(
                phrase_span,
                verb_idx,
            )
            scores.append((phrase_span, phrase_difficulty))
        return scores

    def calculate_verb_phrase_complexity(
        self,
        phrase: SpanProtocol,
        verb_idx: int,
    ) -> float:
        """
        Calculate the complexity of a given verb phrase.
        """
        noun_chunks = [nc for nc in phrase.noun_chunks]
        nc_complexities = np.zeros((len(noun_chunks)), dtype=np.float32)
        for i, noun_chunk in enumerate(noun_chunks):
            nc_complexity = self.calculate_noun_chunk_complexity(noun_chunk)
            nc_complexities[i] = nc_complexity
        verb_position_scalar = self.calculate_verb_position_complexity(
            phrase, verb_idx
        )
        # Cast to python-native float.
        return float((nc_complexities * verb_position_scalar).sum())

    def calculate_noun_chunk_complexity(self, noun_chunk: SpanProtocol) -> int:
        """
        Calculate how difficult comprehension of the given noun chunk is.
        """
        # Remove determiners from consideration.
        relevant_tokens = [
            token for token in noun_chunk if token.pos_ not in ["DET", "PUNCT"]
        ]
        return len(relevant_tokens)

    def calculate_verb_position_complexity(
        self,
        phrase: SpanProtocol,
        verb_idx: int,
    ) -> float:
        """
        Calculate how difficult the verb position makes parsing the sentence.
        Verb position complexity determined by the number of noun chunks that
        precede the verb (where one noun chunk is acceptable).
        """
        preceding_noun_chunks = 0
        for noun_chunk in phrase.noun_chunks:
            if noun_chunk[-1].i < verb_idx:
                preceding_noun_chunks += 1
        # Handle case where no or one noun chunk is preceding the verb.
        if preceding_noun_chunks < 2:
            return 1.0
        return 1.0 + (0.5 * preceding_noun_chunks)
