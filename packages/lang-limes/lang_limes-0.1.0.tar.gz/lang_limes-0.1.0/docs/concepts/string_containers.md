# String Containers
String containers essentially orchestrate the processing pipeline, cache results
of expensive computations, and provide an interface for the user to engage with
analysis results.

Given that we perform most analysis on a sentence-level while most texts consist
of more than a single sentence, LIMES provides two types of string containers,
the **Text** and the **Sentence** container.

## Text
!!! info "Python Implementation"
    Refer to the [API documentation for the Text class](../api/text.md) for more
    information.

The **Text** container provides logic for generating **Sentence** containers for
a given text. It uses the [Parser](parsers.md) to perform token-level analysis
on the given text and to sentencize the text, creating **Sentence** objects for
each sentence.

The user-provided string is processed lazily, i.e. the raw string is only
operated on once the user calls a function that requires analysis results. This
has the *benefit* that the objects don't take forever to create and don't take
up too much memory but it has the *downside* that you won't be notified if the
provided string has issues (e.g. if it is too unclean for the parser to produce
meaningful results) on object creation.

## Sentence
!!! info "Python Implementation"
    Refer to the [API documentation for the Sentence class](../api/sentence.md)
    for more information.

The **Sentence** container allows sentence-level evaluation of your text, as
well as caching analysis results.

### Caching
Both [Barriers and text complexities](complexity.md) are computed lazily, i.e.
only once the user first requests information about them. Keep in mind that this
means that - once they are computed - analysis results stay in memory until the
whole **Sentence** object is garbage-collected.
