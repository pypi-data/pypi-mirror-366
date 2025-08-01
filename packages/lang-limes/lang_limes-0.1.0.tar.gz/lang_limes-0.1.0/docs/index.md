# LIMES Documentation
> This documentation is still under active development and you will run into
  placeholders. Just bear with us while everything is being put in place!

LIMES is a library for performing linguistic analyses on provided texts
regarding their complexity. The goal of this project is to create a tool that
provides actionable insights on how to make written texts easier to comprehend.

Please note that the actual logic for identifying language barriers is
completely language-specific. Because it is a lot of work to develop these
heuristics, the library currently only ships with implemented analyzers for
**German** texts. However, we encourage you to **build your own analyzers**
based on the provided class templates, either for your own use or to
[contribute to the project](contributing.md).

## Installation
You can install this package via pip by running:

```bash
pip install lang-limes
```

!!! failure "Not yet available on PyPI!"
    You currently CAN'T install via pip, the package isn't published yet! If you
    can't wait to try it out for yourself, try building from source using
    [uv](https://docs.astral.sh/uv/).

### Additional Dependencies
The library requires use of a [Parser](concepts/parsers.md). Currently, we only
ship a parser based on [spaCy's](https://spacy.io/) excellent NLP pipeline. This
means that you need to [install a spaCy model](https://spacy.io/usage/models/)
that supports the language you are working with.

## Example Usage
The core concepts we work with are
[string containers](concepts/string_containers.md),
[parsers](concepts/parsers.md), [analyzers](concepts/analyzers.md), and
[barriers](concepts/complexity.md).

You must use a string container to wrap the text you want to analyze. As our
analysis work on a sentence level, you can either manually sentencize and create
separate [Sentence](api/sentence.md) objects or just throw your whole text into
a [Text](api/text.md) object that takes care of sentencization for you.
We will do the latter for the purpose of this example.

```python
from limes import Text, SpacyParser, GermanAnalyzer

analyzer = GermanAnalyzer()

# You can also pass a spacy NLP object instead of the model name.
# Make sure the model you want to use is installed.
parser = SpacyParser(model="de_core_news_sm")

text = Text(
    raw="Das hier ist ein Text. Dieser Text hat mehrere Sätze.",
    analyzer=analyzer,
    parser=parser,
)
```

While we ship a concrete implementation of the
[GermanAnalyzer](api/analyzers/implementations/de/german_analyzer.md), you can also
use the [BaseAnalyzer]() class and plug in your own [BarrierAnalyzer]() and
[ComplexityAnalyzer]() implementations (e.g. for a language other than German).

### Identifying Barriers
Barriers are detected lazily, and results are cached to avoid redundant
computations. [Barriers](api/barrier.md) themselves are a `property` of the
[Text](api/text.md) object.

```python
# You can iterate over the all barriers in the entire text if you want.
for barrier in text.barriers:
    print(barrier.title)
    # Print the actual string of the token.
    print(barrier.affected_tokens)
    # Print the position of the token in the source text.
    print([token.i for token in barrier.affected_tokens])

# You can also iterate over each sentence.
for sentence in text:
    print(sentence.barriers)

# Alternatively, you can also inspect a specific sentence by index.
print(text[1].barriers)
```

Please note that barriers are also language-specific (because different
languages also differ in how they make comprehension "difficult"). Refer to
[the German Barrier overview](api/analyzers/implementations/de/barriers.md) as
an example for localized barriers.


### Calculating Complexities
There are multiple ways in which you can try to approximate language complexity
(see [Complexity Analyzer](concepts/analyzers.md)).

```python
from limes import ComplexityAlgorithm

# Get the average complexity of the text. You can manually set the heuristic.
avg_complexity = text.average_complexity(
    heuristic=ComplexityAlgorithm.AGGREGATED_LOCAL,
)
print(avg_complexity)

# Alternatively, you can get phrase-level complexities.
# These are also lazily computed and cached.
for phrase, complexity in text.local_complexities:
    print(phrase)
    print(complexity)

# You could also iterate over all sentences in the text and get each sentence's
# global complexity.
for sentence in text:
    complexity = sentence.global_complexity(
        heuristic=ComplexityAlgorithm.AGGREGATED_LOCAL,
    )
    print(sentence)
    print(complexity)
```

## Next Steps
A good place to start is to
[get an overview of the concepts](concepts/overview.md) used to build and
configure the whole processing pipeline.

## Currently Supported Languages
|Language|Contributors|
|--------|------------|
|DE|Katja Grosch, Jannik Schmitt, Susanne Wagner|

## Additional Resources
### Word Frequency Lists
#### German
The frequency list for German words was kindly provided by [Projekt Deutscher Wortschatz](https://wortschatz-leipzig.de/de)
of the Universität Leipzig. The unprocessed list included in this repository
(`data/deu_words_2024.txt`) is based on [1]. Please note that it is not based on
the publicly available "Normgrößenkorpora" but was provided on request by the
Leipzig Corpora team under a **CC BY 4.0 license**.

## References
<a id="1">[1]</a>
Leipzig Corpora Collection (2024).
*German news corpus based on material from 2024.*
Leipzig Corpora Collection. Dataset.
https://corpora.uni-leipzig.de/en?corpusId=deu_news_2024
