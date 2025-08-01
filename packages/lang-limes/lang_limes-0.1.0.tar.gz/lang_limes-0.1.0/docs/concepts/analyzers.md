# Analyzers
Analyzers attempt to spot the "Morphosyntactic and Expressive Snags" in the
parsed version of a given text. As explained in the section
[Text Complexity Identifiers](complexity.md), we evaluate these snags from two
separate angles: **Barriers** and **Complexity Scores**.

We provide an **Analyzer** object that provides a way to hide the fact that the
two different kinds of analysis are handled by different components. But there
are effectively two distinct kinds of Analyzers that are being used by the
Analyzer object to do its job.

## Barrier Analyzer
!!! info "Python Implementation"
    Refer to the [API documentation for the BarrierAnalyzer interface](../api/analyzers/barrier_analyzer.md)
    or the [API documentation for the German Barrier Analyzer](../api/analyzers/implementations/de/barrier_analyzer.md)
    for more information.

The **Barrier Analyzer** takes the parser output as its inputs and returns
a list of barriers that were identified within it. It identifies these barriers
by checking the input against a list of rules, trying to spot certain patterns.
These patterns usually consist of syntactic as well as lexical components; that
is why barrier analysis is **completely language-specific**. Each language needs
its own implementation of this analyzer, with its own rules, its own types of
barriers, and so on.

## Complexity Analyzer
!!! info "Python Implementation"
    Refer to the [API documentation for the ComplexityAnalyzer interface](../api/analyzers/complexity_analyzer.md)
    or the [API documentation for the German Complexity Analyzer](../api/analyzers/implementations/de/complexity_analyzer.md)
    for more information.

The **Complexity Analyzer** takes the parser output as its input and returns
either a simple floating-point value encoding the text complexity or a
comprehensive break-down of text components and their respective complexities
(see more about how complexities are calculated in the section
[Text Complexity Identifiers](complexity.md)).

Unlike the **Barrier Analyzer**, the **Complexity Analyzer** is **not fully
language-specific**. It does not require any specific lexical information; it
only evaluates information ordering. This means that the **Complexity Analyzer**
is *technically* specific to a group of languages that share the same word order
in linguistic typology. This means that you may experiment with applying, say,
the [GermanComplexityAnalyzer](../api/analyzers/implementations/de/complexity_analyzer.md)
to non-German texts that follow the same general sentence structure.

!!! tip "Language Structures"
    German is a [V2 word order](https://en.wikipedia.org/wiki/V2_word_order)
    language. This is a trait shared with other Germanic languages. Feel free to
    play around with the `GermanComplexityAnalyzer` in other Germanic languages
    (e.g. Dutch) and see how that works out! Just make sure to use a spaCy model
    that matches the language you're working on for your `SpacyParser`.
