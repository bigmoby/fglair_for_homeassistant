"""Exceptions for FGLair Home Assistant Integration."""


class FGLairBaseException(Exception):
    """Base FGLair component Exception"""

    def __init__(self, *args: object, **kwargs: object):
        if args:
            self.message = args[0]
            super().__init__(*args)
        else:
            self.message = None

        self.custom_kwarg = kwargs.get("custom_kwarg")

    def __str__(self) -> str:
        if self.message:
            return "FGLairBaseException, {0} ".format(self.message)
        else:
            return "FGLairBaseException has been raised"

    def __repr__(self) -> str:
        if self.message:
            return "FGLairBaseException, {0} ".format(self.message)
        else:
            return "FGLairBaseException has been raised"


class FGLairGeneralException(FGLairBaseException):
    """Raise my general exception"""


class FGLairMethodException(FGLairBaseException):
    """Raise wrong method usage exception"""
