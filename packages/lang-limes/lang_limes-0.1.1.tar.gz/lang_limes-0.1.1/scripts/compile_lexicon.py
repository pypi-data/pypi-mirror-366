"""
Module for transforming a raw frequency list into an artifact that can be used
for the `Lexicon` class.
"""

import logging
import re
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from marisa_trie import RecordTrie

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

LOGGER = logging.getLogger("lexicon_compiler")

WORD_REGEX = re.compile(
    # First char: ASCII A–Z or German umlaut/ß.
    r"^[A-Za-zÄÖÜäöüß]"
    # Middle chars: letters, apostrophe or hyphen.
    r"(?:[A-Za-zÄÖÜäöüß'-]*"
    # Last char: must be a letter if length > 1.
    r"[A-Za-zÄÖÜäöüß])?$"
)


@dataclass
class Entry:
    """An entry in the frequency list."""

    word: str
    count: int


def main(source_file: Path, target_file: Path):
    entries = load_frequency_file(source_file=source_file)
    compile_trie(entries=entries, target_file=target_file)


def load_frequency_file(source_file: Path) -> list[Entry]:
    """
    Load data from frequency file.
    """
    entries: list[Entry] = []
    dropped = 0
    LOGGER.info("Attempting to load entries from '%s'.", str(source_file))
    with source_file.open("r", encoding="utf-8") as file:
        for line in file.readlines():
            components = line.split("\t")
            assert len(components) == 2, (
                "Failed to parse file; expected tab-separated tuple."
            )
            if is_word(components[0]):
                entries.append(
                    Entry(
                        word=components[0],
                        count=int(components[1]),
                    )
                )
            else:
                dropped += 1
    LOGGER.info(
        "Loaded %s words, dropped %s entries for failing word-criterion.",
        len(entries),
        dropped,
    )
    return entries


def is_word(token: str) -> bool:
    """
    Checks whether a given string is a word; requirements are that it starts and
    ends with an alphabetical character and only hyphens and apostrophes are
    allowed as non-alphabetical characters between the first and last letters.
    """
    return bool(WORD_REGEX.fullmatch(token))


def compile_trie(entries: list[Entry], target_file: Path):
    """
    Compile a trie object based off the provided entries and persist it at the
    provided location.
    """
    words: list[str] = []
    # Keys need to be tuples for RecordTrie.
    counts: list[tuple[int]] = []
    for entry in entries:
        words.append(entry.word)
        counts.append((entry.count,))
    LOGGER.info("Compiling trie object for %s entries.", len(entries))
    # We format the counts into little-Endian unsigned longs.
    format = "<L"
    trie = RecordTrie(format, zip(words, counts))
    LOGGER.info("Persisting trie at path %s.", str(target_file))
    trie.save(target_file)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Transform a raw frequency list into a trie-like artifact."
    )
    parser.add_argument(
        "source_file",
        type=Path,
        help="Path to the raw frequency list file (tab-separated values).",
    )
    parser.add_argument(
        "target_file",
        type=Path,
        help="Destination path for the compiled trie file.",
    )

    args = parser.parse_args()
    main(source_file=args.source_file, target_file=args.target_file)
