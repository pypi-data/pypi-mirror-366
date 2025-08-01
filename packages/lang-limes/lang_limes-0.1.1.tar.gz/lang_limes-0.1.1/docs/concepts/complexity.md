# Text Complexity Identifiers
We look at text complexity in two different ways:

1. **Concrete Barriers:** Phrases and/or words that, for one reason or another,
make text comprehension more difficult.
2. **Text Complexity Score:** A numerical score that tries to provide a simple metric
to get a feeling for the linguistic complexity of a sentence at a glance.

## Barriers
!!! info "Python Implementation"
    Refer to the [API documentation for the Barrier class](../api/barrier.md)
    for more information.

Conceptually, an **abstract barrier** consists of a *title*, a *category*, a
*description* of what makes the barrier difficult to comprehend, and a
*suggestion* for how to solve the given kind of barrier. A **concrete barrier**,
i.e. an instance of a given barrier type in a text, additionally contains the
*affected tokens* in the given text; these are the parts of the text that
constitute the barrier.

It is important to note that text barriers are not equal in how much they
increase text difficulty; neither different types of abstract barriers, nor two
concrete barriers of the same type! For example, a passive phrase where the two
affected tokens are right beside each other (e.g. "wurde gegessen" in
"Die Banane wurde gegessen.") is much easier to comprehend than a passive phrase
where there is distance between the two tokens (e.g. "wurde gegessen" in "Die
Banane wurde von Anneke und Jonathan gegessen.").

## Text Complexity Score
!!! info "Python Implementation"
    Refer to the [API documentation for the ComplexityAnalyzer class](../api/analyzers/complexity_analyzer.md)
    for more information.

Oh great, [another readability metric](https://en.wikipedia.org/wiki/Readability#Readability_formulas).
But hear us out. Most of the classical scores use some sort of word- or
syllable-length approach to quantify readability. But the fact of the matter is
that you can create incomprehensible sentences using short words only. Moreover,
we don't usually process sentences letter-by-letter. So instead we tried to
quantify complexity based on the [dependency tree](https://en.wikipedia.org/wiki/Dependency_grammar#Syntactic_dependencies)
of the sentence, as it provides insights into how information was structured
within the framework of a given sentence. This means that our complexity score
**encodes structural complexity** much more than "big-words frequency".

## Sentence-wide vs. Phrasal Complexity
We are experimenting with two separate ways of calculating complexity.

While quantifying the complexity of the complete dependency tree of a sentence
(**sentence-wide approach**) seems like a reasonable starting point, this
approach is excessively sensitive to sentence-length; dependency trees of longer
sentences are inherently *larger* than dependency trees of shorter sentences.

That is why we developed a second approach, the **phrasal complexity**. In this
approach, we look at significant nodes of the dependency tree in isolation,
similar to how a reader would process the meaning of a sentence in chunks. We
calculate the complexity of each chunk, and consider these complexities to be
additive in nature. This means that the complexity of a sentence is the sum of
the complexities of its parts. This approach is not quite as sensitive to
sentence length (since a few complex phrases drive the value much more strongly
than a larger number of simple phrases) and allows us to identify parts of a
sentence that most benefit from a rephrasing.

### Why keep both?
While we have found the **phrasal complexity** to be more useful for our use
cases, neither score is battle-tested enough for us to definitively pick the
superior one. Arguably, both scores have their own flaws.

We are publishing both approaches in the hopes that - with increased use - both
scores can be refined to best suit different niches in quantifying text
complexity. On that note, feel free to check out how you can
[contribute](../contributing.md) to the project!
