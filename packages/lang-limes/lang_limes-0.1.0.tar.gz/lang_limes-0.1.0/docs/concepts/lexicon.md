# Lexicons
Barrier detection logic might require processing information regarding whether
a word exists and/or how frequent it is. For this specific use case, the
[`Lexicon` interface](../api/analyzers/lexicon.md) was created to
provide a template for classes that perform such actions. Given the obvious
language specificity of "is x a word?," every language that uses word-frequency-
based heuristics for barrier detection needs to implement its own Lexicon.

A sample implementation for the German language is provided both to provide a
template for how to approach the problem, and because German barrier detection
utilizes word-frequency-based heuristics.

## Language-Specific Implementations
Language-specific implementations of Lexicons evidently need some sourt of
concrete data to draw upon, for example a frequency list of words for the given
language.

!!! important "Handling Language-Specififc Resources"
    Given that the library currently only supports a single language, relevant
    artifacts for barrier detection simply ship with the package as a whole.
    This will likely change to a more nltk-like approach, where required corpora
    are downloaded into a library cache based on a user's request and the
    library itself ships only with the minimum requirements.
    For now you can assume that the library you install contains everything you
    need (other than the spaCy models used for parsing). However, be aware that
    this may change if language support is ever expanded.

The library ships with these artifacts, so no further download is necessary. The
artifacts themselves were pre-compiled to use as little space as possible.


### German
The [`German lexicon`](../api/analyzers/implementations/de/lexicon.md) is a
concrete implementation of the Lexicon interface for the German language.

On a linguistic level, the lexicon uses data which was kindly provided by
[Projekt Deutscher Wortschatz](https://wortschatz-leipzig.de/de) of the
Universität Leipzig and is based on a corpus of news articles.

!!! warning "Domain-Specificity of Word Frequencies"
    Relative frequencies (e.g. when comparing frequencies between two words, as
    is the use case for the German lexicon) are heavily influenced by the domain
    which is being observed.
    This issue does not have an elegant solution and is not something to be
    solved but rather to be mindful of as you design your heuristics.

On a technical level, making a list of roughly 6 million entries accessible for
lookup operations that have to be performed at high volume comes with some
considerations.
While Python dictionaries have constant lookup speeds (good), they also have a
significant memory footprint (bad) when creating dicts of sizes such as the
lexicon.
That is why we have computed a [Marisa-Trie](https://marisa-trie.readthedocs.io/en/latest/)
object to use during lookup. It significantly reduces memory footprint both
in-memory and on disk at the cost of [somewhat worse lookup speeds](https://marisa-trie.readthedocs.io/en/latest/benchmarks.html).

Alternatives to this choice are currently [being evaluated](https://codeberg.org/deepsight/LIMES/issues/3).
