# Overview
At its core, there are four components that make up LIMES:

1. [String Containers](string_containers.md)
2. [Parsers](parsers.md)
3. [Analyzers](analyzers.md)
4. [Text Complexity Identifiers](complexity.md)

The **string container** (either a [Text](../api/text.md) or a
[Sentence](../api/sentence.md)) serves to orchestrate all the required
components; it also provides caching logic so that expensive computations are
not executed twice.

The **parser**, which is attached to the string container, breaks down the raw
string into its morphosyntactic components, i.e. it identifies the role each
token plays in a given sentence on a syntactic level.

The **analyzer** (which actually consists of two components, read more about it
[here](analyzers.md)) takes the output of the parser and uses it to identify
**barriers** as well as linguistic complexity.

## Language Specificity
Both the **parser** and the **analyzer** must be language-specific. Because this
library ships with a parser built on top of [spaCy](https://spacy.io), you can
easily instantiate a parser that supports your language of choice so long as
spaCy provides a [model](https://spacy.io/models/) for it.

Extending language support for **analyzers** involves significantly more
overhead by comparison. Please refer to the [Analyzer overview](analyzers.md) to
get more information.
