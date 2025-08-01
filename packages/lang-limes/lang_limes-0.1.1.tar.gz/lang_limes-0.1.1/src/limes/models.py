# SPDX-FileCopyrightText: 2025 Jannik Schmitt <jannik.schmitt@deepsight.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Module for domain models."""

from copy import deepcopy
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from limes.protocols import TokenProtocol


class BarrierCategorization(Enum):
    """The category to which a barrier belongs."""


class Barrier(BaseModel):
    """A text barrier that consists of one or more tokens."""

    # Allow arbitrary types for compatibility with TokenProtocol.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = Field(description="The title of the barrier.")
    category: BarrierCategorization = Field(
        description=(
            "The category of the barrier; the set of barrier categories is "
            "language-specific."
        ),
    )
    description: str = Field(
        description=(
            "A short description of how the barriere impedes text "
            "comprehension."
        ),
    )
    suggested_improvement: str = Field(
        description="How best to resolve the type of the given barrier.",
    )
    affected_tokens: list[TokenProtocol] | None = Field(
        default=None,
        description="The tokens in a given text that are part of the barrier.",
    )

    def copy_with(self, affected_tokens: list[TokenProtocol] | None):
        """
        Create a deep copy of the Barrier instance and optionally overwrite
        'affected_tokens'.
        """
        new_barrier = deepcopy(self)
        new_barrier.affected_tokens = affected_tokens
        return new_barrier


class SyntaxDescription(BaseModel):
    """An overview of the syntax of a given string."""

    backwards_dependencies_count: int
    mean_backwards_dependency_length: float
    forward_dependencies_count: int
    mean_forward_dependency_length: float
    max_dependency_depth: int
    dependency_head_count: int
    noun_chunk_count: int
    comma_count: int
    max_children: int
    biggest_root_relative_position: float


class ComplexityAlgorithm(Enum):
    """
    The heuristic according to which the complexity of a sentence is to be
    quantified. `GLOBAL` uses an algorithm that evaluates a sentence as a
    monolith; `AGGREGATED_LOCAL` uses an algorithm that calculates phrasal
    complexity for each phrase in a given sentence, and then aggregates these
    values.
    """

    GLOBAL = "global"
    AGGREGATED_LOCAL = "aggregated_local"


class Direction(Enum):
    """
    Class encoding the direction of a syntactic dependency. A LEFT dependency is
    a dependency where solving the dependency requires looking to the left of
    the root, i.e. at a previous word. A RIGHT dependency can be resolved by
    looking forwad, i.e. at a following word.
    """

    LEFT = -1
    RIGHT = 1


class Dependency:
    """
    A dependency between a root and its child. The root is a word that requires
    taking into consideration the child in order to properly parse the meaning
    of the root.
    """

    def __init__(self, depth: int, root_idx: int, child_idx: int):
        """
        Create a Dependency object.

        Parameters
        ----------
        depth : int
            The depth of the dependency in the dependency tree.
        root_idx : int
            The index of the dependency root in the given sentence.
        child_idx : int
            The index of the dependency child in the given sentence.
        """
        if root_idx < child_idx:
            self.length = child_idx - root_idx
            self.direction = Direction.RIGHT
        elif root_idx > child_idx:
            self.length = root_idx - child_idx
            self.direction = Direction.LEFT
        else:
            raise RuntimeError(
                "Indeces of root and child must not be identical!",
            )
        self.root_idx = root_idx
        self.child_idx = child_idx
        self.depth = depth

    def __repr__(self):
        return (
            f"Dependency(root={self.root_idx}, "
            f"child={self.child_idx}, "
            f"depth={self.depth})"
        )
