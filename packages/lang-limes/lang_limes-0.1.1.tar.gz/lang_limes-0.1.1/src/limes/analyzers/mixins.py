# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
from statistics import mean

import numpy as np

from limes.errors import RootNotFoundError
from limes.models import Dependency, Direction, SyntaxDescription
from limes.protocols import DocumentProtocol, SpanProtocol, TokenProtocol


class SyntaxAnalyzerMixin:
    """
    A mixin that adds functionality to do downstream syntactic analysis on
    objects that were parsed by a `Parser` object.
    """

    def build_dependencies_list(
        self,
        sentence: DocumentProtocol,
    ) -> list[Dependency]:
        """
        Parse the dependency structure of a sentence and create a list of
        Dependency objects describing the relationship between words.
        """
        dependency_heads = {token.head.i for token in sentence}
        is_processed = np.array([False] * len(sentence))
        # Since the first index in a span may be > 0, normalize references to
        # the processed list.
        index_normalizer = sentence[0].i
        dependencies = []
        for head_idx in dependency_heads:
            depth = 0
            is_processed[head_idx - index_normalizer] = True
            token = sentence[head_idx - index_normalizer]
            children = [(token, child) for child in token.children]
            while children:
                depth += 1
                next_children = []
                for root, child in children:
                    if (
                        is_processed[child.i - index_normalizer] is True
                        or child.is_punct
                    ):
                        continue
                    is_processed[child.i - index_normalizer] = True
                    next_children += [(child, c) for c in child.children]
                    dependency = Dependency(depth, root.i, child.i)
                    dependencies.append(dependency)
                children = next_children
        return dependencies

    def evaluate_syntax(
        self,
        sentence: DocumentProtocol,
        dependencies: list[Dependency] | None = None,
    ) -> SyntaxDescription:
        """
        Create a list of statistics about the syntactic makeup of the sentence.
        """
        backwards_dependencies = []
        forwards_dependencies = []
        if dependencies is None:
            dependencies = self.build_dependencies_list(sentence)

        for dependency in dependencies:
            match dependency.direction:
                case Direction.LEFT:
                    backwards_dependencies.append(dependency)
                case Direction.RIGHT:
                    forwards_dependencies.append(dependency)

        max_children = 0
        max_idx = 0
        for token in sentence:
            num_children = len(list(c for c in token.children))
            if num_children >= max_children:
                max_children = num_children
                max_idx = token.i

        return SyntaxDescription(
            forward_dependencies_count=len(forwards_dependencies),
            mean_forward_dependency_length=self._get_mean_dependency_length(
                forwards_dependencies
            ),
            backwards_dependencies_count=len(backwards_dependencies),
            mean_backwards_dependency_length=self._get_mean_dependency_length(
                backwards_dependencies
            ),
            max_dependency_depth=max(dep.depth for dep in dependencies),
            dependency_head_count=len([token.head.i for token in sentence]),
            noun_chunk_count=len(list(sentence.noun_chunks)),
            comma_count=len([token for token in sentence if token.text == ","]),
            max_children=max_children,
            biggest_root_relative_position=max_idx / len(sentence),
        )

    def _get_mean_dependency_length(
        self,
        dependencies: list[Dependency],
    ) -> float:
        """
        Identify mean dependency length of dependency list. Returns 0 if no
        dependencies are present.
        """
        if len(dependencies) > 0:
            return mean([dep.length for dep in dependencies])
        return 0.0

    def identify_verb_phrases(
        self,
        sentence: DocumentProtocol,
    ) -> dict[int, list[int]]:
        """
        Identify spans that make up individual verb phrases, excluding
        coordinating conjunctions.
        """
        root_index = self.find_root_index(sentence)
        verb_ids = self.identify_verb_indices(sentence, root_index)
        phrases = {}
        for verb_idx in verb_ids:
            phrases[verb_idx] = self._parse_subtree(
                sentence,
                verb_idx,
                verb_ids,
            )
        return phrases

    def find_root_index(
        self,
        sentence: DocumentProtocol,
    ) -> int:
        """
        Identify the token that is parent to all other tokens in the sentence's
        dependency tree.
        """
        for token in sentence:
            ancestors = [ancestor for ancestor in token.ancestors]
            if len(ancestors) == 0:
                return token.i
        raise RootNotFoundError("No root identified!")

    def identify_verb_indices(
        self,
        sentence: DocumentProtocol,
        root_idx: int,
    ) -> list[int]:
        """
        Identify tokens that are main verbs. This function also considers verbs
        that spaCy might have mislabelled as auxiliary verbs.
        """
        verb_ids = []
        for token in sentence:
            if token.pos_ == "VERB":
                ancestor_pos = [
                    sentence[i].pos_
                    for i in self._get_immediate_ancestors(
                        token,
                    )
                ]
                if "AUX" not in ancestor_pos:
                    verb_ids.append(token.i)
            elif token.pos_ == "AUX":
                if token.i == root_idx:
                    verb_ids.append(token.i)
                    continue
                children_deps = [child.dep_ for child in token.children]
                if "pd" in children_deps or "oc" in children_deps:
                    verb_ids.append(token.i)
        return verb_ids

    def _get_immediate_ancestors(self, token: TokenProtocol) -> list[int]:
        """
        Identify the immediate ancestor of a given token in the Sentence.
        """
        return [
            ancestor.i
            for ancestor in token.ancestors
            if str(token) in [str(child) for child in ancestor.children]
        ]

    def _parse_subtree(
        self,
        sentence: DocumentProtocol,
        subtree_root_id: int,
        verb_ids: list[int],
    ) -> list[int]:
        """
        Create a list of each token that is a descendant of the provided subtree
        root while not being a subtree root itself.
        """
        phrase = set()
        conjuncts = []
        modifiers = []
        potential_subclause_roots = []
        for descendant in sentence[subtree_root_id].subtree:
            if descendant.dep_ == "cd":
                conjuncts.append(descendant.i)
            elif descendant.dep_ == "mo" and descendant.i != subtree_root_id:
                modifiers.append(descendant.i)
            elif (
                descendant.dep_.endswith("c")
                and descendant.i in verb_ids
                and not descendant.i == subtree_root_id
            ):
                potential_subclause_roots.append(descendant.i)
            elif descendant.dep_ == "rc" and descendant.i != subtree_root_id:
                potential_subclause_roots.append(descendant.i)
            # Skip final punctuation in phrase.
            elif descendant.is_punct:
                continue
            phrase.add(descendant.i)
        independent_tokens = set()
        # Remove relative clauses from subtree.
        for clause_root in potential_subclause_roots:
            relative_clause = {
                token.i for token in sentence[clause_root].subtree
            }
            independent_tokens.update(relative_clause)
        # Check conjuncts and modifiers to evaluate if they connect to a
        # different coherent subtree.
        for potential_phrase_transition in [modifiers, conjuncts]:
            for token in potential_phrase_transition:
                coherent_subtree = self._identify_coherent_subtree_elements(
                    sentence,
                    token,
                    verb_ids,
                )
                if coherent_subtree:
                    independent_tokens.update(coherent_subtree)
        isolated_phrase = phrase - independent_tokens
        return list(isolated_phrase)

    def _identify_coherent_subtree_elements(
        self,
        sentence: DocumentProtocol,
        subtree_root_id: int,
        verb_idx: list[int],
    ) -> set[int] | None:
        """
        Assemble a subtree from the specified root ID downward and check if the
        resulting subtree is coherent, i.e. constituting a verb phrase.
        """
        is_coherent_subtree = False
        subtree = {subtree_root_id}
        for descendant in sentence[subtree_root_id].subtree:
            if descendant.i in verb_idx:
                is_coherent_subtree = True
            subtree.add(descendant.i)
        if subtree_root_id in verb_idx:
            is_coherent_subtree = True
        if is_coherent_subtree:
            return subtree
        return None

    def phrase_idx_to_span(
        self,
        sentence: DocumentProtocol,
        phrase_idx: list[int],
    ) -> SpanProtocol:
        """
        Creates a Span object from a list of involved indices.
        """
        phrase_idx.sort()
        return sentence.span(
            start_idx=phrase_idx[0],
            end_idx=phrase_idx[-1] + 1,
        )
