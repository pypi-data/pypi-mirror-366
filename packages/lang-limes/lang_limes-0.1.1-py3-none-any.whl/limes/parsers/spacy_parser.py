# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Iterable, Iterator

import spacy
from spacy.language import Language
from spacy.tokens import Doc as SpacyDoc
from spacy.tokens import Span as SpacySpan
from spacy.tokens import Token as SpacyToken

from limes.parsers.interfaces import Parser
from limes.protocols import (
    DocumentProtocol,
    SpanProtocol,
    TokenProtocol,
)


class SpacyTokenAdapter(TokenProtocol):
    """
    A token in a text. The token contains both of its string literal (i.e. the
    word) as well as its metadata (e.g. its part of speech, its position in the
    sentence etc.).
    The TokenAdapter wraps around a spaCy Token object to only expose
    attributes that adhere to the
    """

    def __init__(self, token: SpacyToken):
        self._token = token

    def __repr__(self) -> str:
        return f"SpacyToken({str(self)})"

    def __str__(self) -> str:
        """The text of the token."""
        return self._token.text

    @property
    def text(self) -> str:
        """The text of the token."""
        return self._token.text

    @property
    def morph(self) -> dict[str, str]:
        """The morphological analysis of the string token."""
        return self._token.morph.to_dict()

    @property
    def pos_(self) -> str:
        """
        The part-of-speech tag of the given token (based on the Universal POS
        tagset).
        """
        return self._token.pos_

    @property
    def fine_pos(self) -> str:
        """
        The part-of-speech tag of the given token based on a language-specific
        tagset - if available for the given language.
        """
        return self._token.tag_

    @property
    def dep_(self) -> str:
        """The dependency tag of the given token."""
        return self._token.dep_

    @property
    def lemma_(self) -> str:
        """The lemma of the word contained within the given token."""
        # Added robustness in cases where spacy fails to correctly identify the
        # lemma.
        if self._token.lemma_ == "--":
            return str(self._token).lower()
        return self._token.lemma_.lower()

    @property
    def i(self) -> int:
        """
        The index of the token within the context of the document that contains
        it, where a document can be considered as a list of tokens.
        """
        return self._token.i

    @property
    def head(self) -> "SpacyTokenAdapter":
        """The syntactic parent of the given token."""
        return SpacyTokenAdapter(self._token.head)

    @property
    def is_punct(self) -> bool:
        """Whether or not the given token is punctuation."""
        return self._token.is_punct

    @property
    def children(self) -> Iterable["SpacyTokenAdapter"]:
        """
        All tokens that constitutes descendants of the given token in the
        dependency tree of the document.
        """
        return (SpacyTokenAdapter(c) for c in self._token.children)

    @property
    def ancestors(self) -> Iterable["SpacyTokenAdapter"]:
        """
        All tokens that constitute ancestors of the given token in the
        dependency tree of the document.
        """
        return (SpacyTokenAdapter(c) for c in self._token.ancestors)

    @property
    def subtree(self) -> Iterable["SpacyTokenAdapter"]:
        """
        The given token as well as all its descendants in the dependency tree
        of the given document.
        """
        return (SpacyTokenAdapter(c) for c in self._token.subtree)


class SpacySpanAdapter(SpanProtocol):
    def __init__(self, span: SpacySpan):
        self._span = span

    def __repr__(self) -> str:
        return f"SpacySpanAdapter({self.text})"

    @property
    def text(self) -> str:
        """The actual text of the tokens contained within the span."""
        return self._span.text

    @property
    def noun_chunks(self) -> Iterable["SpacySpanAdapter"]:
        """
        All noun chunks contained in the given span; a noun chunk is another
        span consisting of one or more nouns and - optionally - adjectives
        and/or auxiliary verbs.
        """
        # spaCy Span.noun_chunks yields raw SpacySpan
        return (SpacySpanAdapter(nc) for nc in self._span.noun_chunks)

    def __iter__(self) -> Iterator[SpacyTokenAdapter]:
        """
        Iterate over the Span, one token at a time. Iteration happens in
        the direction common in reading the language (e.g. "left to right" in
        German or English).
        """
        # iterate over TokenAdapter
        yield from (SpacyTokenAdapter(tok) for tok in self._span)

    def __getitem__(self, i: int) -> SpacyTokenAdapter:
        """Retrieve the i-th token in the provided span."""
        return SpacyTokenAdapter(self._span[i])


class SpacyDocumentAdapter(DocumentProtocol):
    def __init__(self, doc: SpacyDoc):
        self._doc = doc

    def __repr__(self) -> str:
        return f"SpacyDocumentAdapter({self.text})"

    @property
    def text(self) -> str:
        """The text contained in the given document."""
        return self._doc.text

    @property
    def noun_chunks(self) -> Iterable[SpacySpanAdapter]:
        """
        All noun chunks contained in the given document; a noun chunk is a span
        consisting of one or more nouns and - optionally - adjectives and/or
        auxiliary verbs.
        """
        return (SpacySpanAdapter(nc) for nc in self._doc.noun_chunks)

    @property
    def sents(self) -> Iterator["SpacyDocumentAdapter"]:
        """
        All sentences contained in the provided document. Any sentence is
        considered to be a document.
        """
        yield from (
            SpacyDocumentAdapter(sent.as_doc()) for sent in self._doc.sents
        )

    def __iter__(self) -> Iterator[SpacyTokenAdapter]:
        """
        Iterate over the document, one token at a time. Iteration happens in
        the direction common in reading the language (e.g. "left to right" in
        German or English).
        """
        yield from (SpacyTokenAdapter(tok) for tok in self._doc)

    def __getitem__(self, i) -> SpacyTokenAdapter:
        """Retrieve the i-th token in the provided document."""
        return SpacyTokenAdapter(self._doc[i])

    def __len__(self) -> int:
        """
        The length of the document, as counted by the number of tokens (i.e.
        distinct words or punctuation marks) contained within it.
        """
        return len(self._doc)

    def span(self, start_idx: int, end_idx: int) -> SpacySpanAdapter:
        """
        Create a span of all tokens between the start index and the end index
        provided.
        """
        return SpacySpanAdapter(self._doc[start_idx:end_idx])


class SpacyParser(Parser):
    """
    A Parser that performs morphosyntactic analysis on a raw string and returns
    an instance of a concrete implementation of the `DocumentProtocol`.
    """

    def __init__(self, model: Language | str = "de_dep_news_trf"):
        if isinstance(model, str):
            try:
                self._nlp = spacy.load(model)
            except OSError as error:
                raise ValueError(
                    f"Model '{model}' not found. Try downloading it by running "
                    f"`python -m spacy download {model}`."
                ) from error
        else:
            self._nlp = model
        if "sentencizer" not in [step[0] for step in self._nlp.pipeline]:
            self._nlp.add_pipe("sentencizer")

    def __call__(self, text: str) -> DocumentProtocol:
        """
        Create a SpacyDocument out of the provided string.
        """
        return SpacyDocumentAdapter(self._nlp(text))
