# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
# flake8: noqa: E501
# pylint: disable=missing-function-docstring, missing-param-doc, missing-raises-doc
# pylint: disable=line-too-long, import-outside-toplevel
"""Command line interface to convert or run a waldiez file."""

import json
import os
from pathlib import Path
from typing import Optional

import anyio
import typer
from dotenv import load_dotenv
from typing_extensions import Annotated

from .cli_extras import add_cli_extras
from .logger import get_logger
from .models import Waldiez
from .utils import get_waldiez_version

load_dotenv()
LOG = get_logger()

app = typer.Typer(
    name="waldiez",
    help="Handle Waldiez flows.",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    },
    add_completion=False,
    no_args_is_help=True,
    invoke_without_command=True,
    add_help_option=True,
    pretty_exceptions_enable=False,
    epilog="Use `waldiez [COMMAND] --help` for command-specific help.",
)


@app.callback()
def show_version(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show the version of the Waldiez package.",
    ),
) -> None:
    """Show the version of the Waldiez package and exit."""
    if version:
        typer.echo(f"waldiez version: {get_waldiez_version()}")
        raise typer.Exit()


@app.command()
def run(
    file: Annotated[
        Path,
        typer.Option(
            ...,
            help="Path to the Waldiez flow (*.waldiez) file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    output: Optional[Path] = typer.Option(  # noqa: B008
        None,
        help=(
            "Path to the output (.py) file. "
            "The output's directory will contain "
            "the generated flow (.py) and any additional generated files."
        ),
        dir_okay=False,
        resolve_path=True,
    ),
    uploads_root: Optional[Path] = typer.Option(  # noqa: B008
        None,
        help=(
            "Path to the uploads root directory. "
            "The directory will contain "
            "any uploaded files."
        ),
        dir_okay=True,
        resolve_path=True,
    ),
    structured: bool = typer.Option(  # noqa: B008
        False,
        help=(
            "If set, the output will be structured as a directory with "
            "the flow file and any additional generated files in it."
        ),
    ),
    force: bool = typer.Option(  # noqa: B008
        False,
        help="Override the output file if it already exists.",
    ),
    env_file: Optional[Path] = typer.Option(  # noqa: B008
        None,
        "--env-file",
        "-e",
        help=(
            "Path to a .env file containing additional environment variables. "
            "These variables will be set before running the flow."
        ),
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
) -> None:
    """Run a Waldiez flow."""
    os.environ["AUTOGEN_USE_DOCKER"] = "0"
    os.environ["NEP50_DISABLE_WARNING"] = "1"
    output_path = _get_output_path(output, force)
    from waldiez.runner import WaldiezRunner

    try:
        runner = WaldiezRunner.load(file)
    except FileNotFoundError as error:
        typer.echo(f"File not found: {file}")
        raise typer.Exit(code=1) from error
    except json.decoder.JSONDecodeError as error:
        typer.echo("Invalid .waldiez file. Not a valid json?")
        raise typer.Exit(code=1) from error
    except ValueError as error:
        typer.echo(f"Invalid .waldiez file: {error}")
        raise typer.Exit(code=1) from error
    if runner.is_async:
        anyio.run(
            runner.a_run,
            output_path,
            uploads_root,
            structured,  # structured_io
            False,  # skip_mmd
            False,  # skip_timeline
            env_file,
        )
    else:
        runner.run(
            output_path=output_path,
            uploads_root=uploads_root,
            structured_io=structured,
            skip_mmd=False,
            skip_timeline=False,
            dot_env=env_file,
        )


@app.command()
def convert(
    file: Annotated[
        Path,
        typer.Option(
            ...,
            help="Path to the Waldiez flow (*.waldiez) file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    output: Path | None = typer.Option(  # noqa: B008
        default=None,
        help=(
            "Path to the output file. "
            "The file extension determines the output format: "
            "`.py` for Python script, `.ipynb` for Jupyter notebook."
            " If not provided, the output (.py) will be saved in the same directory as the input file."
            " If the file already exists, it will not be overwritten unless --force is used."
        ),
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    force: bool = typer.Option(
        False,
        help="Override the output file if it already exists.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging.",
        is_eager=True,
        rich_help_panel="Debug",
    ),
) -> None:
    """Convert a Waldiez flow to a Python script or a Jupyter notebook."""
    _get_output_path(output, force)
    with file.open("r", encoding="utf-8") as _file:
        try:
            data = json.load(_file)
        except json.decoder.JSONDecodeError as error:
            typer.echo("Invalid .waldiez file. Not a valid json?")
            raise typer.Exit(code=1) from error
    waldiez = Waldiez.from_dict(data)
    from waldiez.exporter import WaldiezExporter

    exporter = WaldiezExporter(waldiez)
    if debug:
        LOG.set_level("DEBUG")
    if output is None:
        output = Path(file).with_suffix(".py").resolve()
    exporter.export(
        output,
        force=force,
        debug=debug,
    )
    generated = str(output).replace(os.getcwd(), ".")
    typer.echo(f"Generated: {generated}")


@app.command()
def check(
    file: Annotated[
        Path,
        typer.Option(
            ...,
            help="Path to the Waldiez flow (*.waldiez) file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> None:
    """Validate a Waldiez flow."""
    with file.open("r", encoding="utf-8") as _file:
        data = json.load(_file)
    Waldiez.from_dict(data)
    LOG.success("Waldiez flow seems valid.")


def _get_output_path(output: Optional[Path], force: bool) -> Optional[Path]:
    if output is not None:
        output = Path(output).resolve()
    if output is not None and not output.parent.exists():
        output.parent.mkdir(parents=True)
    if output is not None and output.exists():
        if not force:
            LOG.error("Output file already exists.")
            raise typer.Exit(code=1)
        output.unlink()
    return output


add_cli_extras(app)

if __name__ == "__main__":
    app()
