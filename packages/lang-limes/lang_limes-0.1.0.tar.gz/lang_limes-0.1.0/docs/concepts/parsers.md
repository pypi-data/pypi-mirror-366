# Parsers
!!! info "Python Implementation"
    Refer to the [API documentation for the Parser interface](../api/parsers/interface.md)
    and the [API documentation for the SpacyParser implementation](../api/parsers/spacy_parser.md)
    for more information.

Parsers turn texts from strings into morphosyntactic information. They perform
**tokenization**, **lemmatization**, **dependency parsing**, **part-of-speech
tagging**, and **sentencization**. Effectively, they translate the flat string
of a text into a set of hierarchical objects that can be used to interpret how
the text is structured.

!!! info "Python Implementation"
    Refer to the [API documentation for the relevant protocols](../api/protocols.md)
    for more information.

Parsing is a necessary first step in identifying language barriers because the
parser "translates" the input text into the kind of information that the
[Analyzer](analyzers.md) will operate on to perform its analysis.

Automated parsing is incredibly complex, and the output is sometimes just
right-ish. We decided against building our parser from scratch because that is
a problem domain much larger than the one we are operating in. Luckily, the team
over at [explosion AI](https://explosion.ai/) has built a
[comprehensive library](https://spacy.io/) for this purpose that (a) suits our
purpose and (b) comes with a lot of models that provide support for a variety of
languages. That is why we have **built our concrete Parser implementation on top
of spaCy**. However, we have provided implementation-agnostic interfaces so that
it is easy to build an alternative implementation; parsing and barrier analysis
are separate problem domains and we want to be able to develop and ship
domain-specific solutions without having to deal with unfortunate dependencies.
