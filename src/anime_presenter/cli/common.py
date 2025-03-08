import functools
import sys
import typing as t
from typing import Callable

import typer

ExceptionType = t.Type[Exception]
ErrorHandlingCallback = Callable[[Exception], int]


class ErrorHandlingTyper(typer.Typer):

    @functools.wraps(typer.Typer.__init__)
    def __init__(self, *args, **kwargs) -> None:
        self.error_handlers: t.Dict[ExceptionType, ErrorHandlingCallback] = {}
        super().__init__(*args, **kwargs)

    def error_handler(self, *exceptions: ExceptionType):

        def decorator(
            f: ErrorHandlingCallback,
        ):
            for exc in exceptions:
                self.error_handlers[exc] = f

            return f

        return decorator

    def __call__(self, *args, **kwargs):
        try:
            super().__call__(*args, **kwargs)
        except Exception as e:
            try:
                callback = self.error_handlers[type(e)]
                exit_code = callback(e)
                raise typer.Exit(code=exit_code)
            except typer.Exit as e:
                sys.exit(e.exit_code)
            except KeyError:
                raise e
