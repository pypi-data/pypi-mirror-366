"""Exceptions for FUSOR models and helper functions."""


class IDTranslationException(Exception):  # noqa: N818
    """Indicate translation failure for provided ID value"""


class FUSORParametersException(Exception):  # noqa: N818
    """Signal incorrect or insufficient parameters for model constructor methods."""
