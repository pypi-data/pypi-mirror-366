# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
from abc import ABC, abstractmethod

from limes.protocols import DocumentProtocol


class Parser(ABC):
    """
    A Parser that performs morphosyntactic analysis on a raw string and returns
    an instance of a concrete implementation of the `DocumentProtocol`.
    """

    @abstractmethod
    def __call__(self, text: str) -> DocumentProtocol:
        pass
