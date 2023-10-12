"""Utilities for FGLair Home Assistant Integration."""


def isNotBlank(test_string: str | None) -> bool:
    return bool(test_string and test_string.strip())


def isBlank(test_string: str | None) -> bool:
    return not (test_string and test_string.strip())
