# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
"""
Module for implementation-agnostic interface definitions that are shared across
submodules.
"""

from typing import Iterable, Iterator, Protocol, runtime_checkable


@runtime_checkable
class TokenProtocol(Protocol):
    """
    A token in a text. The token contains both of its string literal (i.e. the
    word) as well as its metadata (e.g. its part of speech, its position in the
    sentence etc.).
    """

    def __str__(self) -> str:
        """The text of the token."""
        ...

    def text(self) -> str:
        """The text of the token."""
        ...

    @property
    def morph(self) -> dict[str, str]:
        """The morphological analysis of the string token."""
        ...

    @property
    def pos_(self) -> str:
        """
        The part-of-speech tag of the given token (based on the Universal POS
        tagset).
        """
        ...

    @property
    def fine_pos(self) -> str | None:
        """
        The part-of-speech tag of the given token based on a language-specific
        tagset - if available for the given language.
        """
        ...

    @property
    def dep_(self) -> str:
        """The dependency tag of the given token."""
        ...

    @property
    def lemma_(self) -> str:
        """The lemma of the word contained within the given token."""
        ...

    @property
    def i(self) -> int:
        """
        The index of the token within the context of the document that contains
        it, where a document can be considered as a list of tokens.
        """
        ...

    @property
    def is_punct(self) -> bool:
        """Whether or not the given token is punctuation."""
        ...

    @property
    def head(self) -> "TokenProtocol":
        """The syntactic parent of the given token."""
        ...

    @property
    def children(self) -> Iterable["TokenProtocol"]:
        """
        All tokens that constitutes descendants of the given token in the
        dependency tree of the document.
        """
        ...

    @property
    def ancestors(self) -> Iterable["TokenProtocol"]:
        """
        All tokens that constitute ancestors of the given token in the
        dependency tree of the document.
        """
        ...

    @property
    def subtree(self) -> Iterable["TokenProtocol"]:
        """
        The given token as well as all its descendants in the dependency tree
        of the given document.
        """
        ...


@runtime_checkable
class SpanProtocol(Protocol):
    """
    A span of tokens in a text. The span contains references to the tokens it
    contains, as well as information about noun chunks that are part of the
    given span.
    """

    @property
    def text(self) -> str:
        """The actual text of the tokens contained within the span."""
        ...

    @property
    def noun_chunks(self) -> Iterable["SpanProtocol"]:
        """
        All noun chunks contained in the given span; a noun chunk is another
        span consisting of one or more nouns and - optionally - adjectives
        and/or auxiliary verbs.
        """
        ...

    def __iter__(self) -> Iterator[TokenProtocol]:
        """
        Iterate over the Span, one token at a time. Iteration happens in
        the direction common in reading the language (e.g. "left to right" in
        German or English).
        """
        ...

    def __getitem__(self, i: int) -> TokenProtocol:
        """Retrieve the i-th token in the provided span."""
        ...


@runtime_checkable
class DocumentProtocol(Protocol):
    """
    A document of text. The document contains both its string literal (i.e. its
    text) as well as related morphosyntactic metadata."""

    @property
    def text(self) -> str:
        """The text contained in the given document."""
        ...

    @property
    def noun_chunks(self) -> Iterable[SpanProtocol]:
        """
        All noun chunks contained in the given document; a noun chunk is a span
        consisting of one or more nouns and - optionally - adjectives and/or
        auxiliary verbs.
        """
        ...

    @property
    def sents(self) -> Iterable["DocumentProtocol"]:
        """
        All sentences contained in the provided document. The concrete
        logic of the class implementing DocumentProtocol must contain
        sentencization logic. Any sentence is considered to be a document.
        """
        ...

    def __iter__(self) -> Iterator[TokenProtocol]:
        """
        Iterate over the document, one token at a time. Iteration happens in
        the direction common in reading the language (e.g. "left to right" in
        German or English).
        """
        ...

    def __getitem__(self, i: int) -> TokenProtocol:
        """Retrieve the i-th token in the provided document."""
        ...

    def __len__(self) -> int:
        """
        The length of the document, as counted by the number of tokens (i.e.
        distinct words or punctuation marks) contained within it.
        """
        ...

    def span(self, start_idx: int, end_idx: int) -> SpanProtocol:
        """
        Create a span of all tokens between the start index and the end index
        provided.
        """
        raise NotImplementedError
