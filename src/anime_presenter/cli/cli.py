import pathlib

import pydantic
import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from typing_extensions import Annotated

from anime_presenter.cli.common import ErrorHandlingTyper
from anime_presenter.markup import Markup
from anime_presenter.pdf_building import save_to_pdf
from anime_presenter.player import Player

console = Console()
app = ErrorHandlingTyper(rich_markup_mode="rich")


@app.callback()
def common_options(
    enable_logs: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        is_flag=True,
    ),
):
    if enable_logs:
        logger.enable("anime_presenter")
        logger.debug("Debug enabled")


@app.error_handler(
    pydantic.ValidationError,
)
def validation_error_handler(error: pydantic.ValidationError) -> int:
    console.print(Panel(str(error), border_style="red", title=error.__class__.__qualname__))
    return 1


@app.command()
def show(
    markup_file: Annotated[
        pathlib.Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
):
    markup = Markup.from_yaml(markup_file)
    with Player.from_markup(markup).open() as player:
        player.loop()


@app.command()
def pdf(
    markup_file: Annotated[
        pathlib.Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    output_file: Annotated[
        pathlib.Path,
        typer.Argument(
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
):

    markup = Markup.from_yaml(markup_file)
    save_to_pdf(markup, output_file)
