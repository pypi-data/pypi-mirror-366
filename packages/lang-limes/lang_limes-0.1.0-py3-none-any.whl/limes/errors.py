"""Module for non-standard errors that might be raised."""


class RootNotFoundError(Exception):
    """
    Error for cases where parsing failed to identify a root verb in a sequence
    of words, either because none is present or because the parsing incorrectly
    misidentified an existing root verb.
    """

    ...
