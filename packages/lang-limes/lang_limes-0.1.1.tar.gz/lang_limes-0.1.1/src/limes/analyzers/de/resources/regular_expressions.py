# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
"""
Lists of regular expressions used to identify whether a token matches a given
pattern.
"""

import re

# Suffixes were lifted from InProD2 guidelines.
ADJECTIVE_SUFFIXES = [
    re.compile(r"(\w+)dicht"),
    re.compile(r"(\w+)komponentig"),
    re.compile(r"(\w+)geheftet"),
    re.compile(r"(\w+)variabel"),
    re.compile(r"(\w+)bestückt"),
    re.compile(r"(\w+)dicht"),
    re.compile(r"(\w+)echt"),
    re.compile(r"(\w+)breit"),
    re.compile(r"(\w+)vernetzt"),
    re.compile(r"(\w+)abweisend"),
    re.compile(r"(\w+)bar"),
    re.compile(r"(\w+)haltig"),
    re.compile(r"(\w+)beständig"),
    re.compile(r"(\w+)fest"),
    re.compile(r"(\w+)resistent"),
    re.compile(r"(\w+)abhängig"),
]

NEGATION_AFFIXES = {
    "prefix": [
        re.compile(r"un(\w+)"),
        re.compile(r"in(\w+)"),
        re.compile(r"ir(\w+)"),
        re.compile(r"il(\w+)"),
        re.compile(r"dis(\w+)"),
        re.compile(r"des(\w+)"),
        re.compile(r"non(\w+)"),
        re.compile(r"a(\w+)"),
    ],
    "suffix": [
        re.compile(r"(\w+)frei(heit)?"),
        re.compile(r"(\w+)los(igkeit)?"),
    ],
}

NOUN_PROPERTY_SUFFIXES = [
    re.compile(r"(\w+)heit"),
    re.compile(r"(\w+)ität"),
    re.compile(r"(\w+)keit"),
]
