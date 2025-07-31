"""Command-line interface for obk using classes."""

from __future__ import annotations

from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer

from .containers import Container
from .services import DivisionByZeroError, FatalError


LOG_FILE = Path("obk.log")


def configure_logging(log_file: Path) -> None:
    """Configure root logging to write to ``log_file``."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )


def _global_excepthook(
    exc_type: type[BaseException], exc_value: BaseException, exc_tb
) -> None:
    """Log uncaught exceptions and exit."""
    if issubclass(exc_type, SystemExit):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    logging.getLogger(__name__).critical(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_tb)
    )
    print(
        "[FATAL] Unexpected error occurred. See the log for details.", file=sys.stderr
    )
    sys.exit(1)


sys.excepthook = _global_excepthook


class ObkCLI:
    """Typer-based CLI with dependency injection."""

    def __init__(
        self, log_file: Path = LOG_FILE, container: Container | None = None
    ) -> None:
        self.container = container or Container()
        self.log_file = log_file

        self.app = typer.Typer(
            add_completion=False,
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        self.app.callback()(self._callback)
        self.app.command(
            name="hello-world",
            help="Print hello world",
            short_help="Print hello world",
        )(self._cmd_hello_world)
        self.app.command(
            name="divide",
            help="Divide a by b",
            short_help="Divide two numbers",
        )(self._cmd_divide)
        self.app.command(
            name="fail",
            help="Trigger a fatal error",
            short_help="Trigger a fatal error",
        )(self._cmd_fail)
        self.app.command(
            name="greet",
            help="Greet by name with optional excitement",
            short_help="Greet by name",
        )(self._cmd_greet)

    # callback ---------------------------------------------------------------
    def _callback(
        self, logfile: Path = typer.Option(LOG_FILE, help="Path to the log file")
    ) -> None:
        self.container.config.log_file.from_value(logfile)
        configure_logging(self.container.config.log_file())

    # command implementations -------------------------------------------------
    def _cmd_hello_world(self) -> None:
        greeter = self.container.greeter()
        typer.echo(greeter.hello())

    def _cmd_divide(self, a: float, b: float) -> None:
        divider = self.container.divider()
        result = divider.divide(a, b)
        logging.getLogger(__name__).info("Divide %s by %s = %s", a, b, result)
        typer.echo(result)

    def _cmd_fail(self) -> None:
        raise FatalError("intentional failure")

    def _cmd_greet(self, name: str, excited: bool = False) -> None:
        greeter = self.container.greeter()
        typer.echo(greeter.greet(name, excited))

    # runner ---------------------------------------------------------------
    def run(self, argv: list[str] | None = None) -> None:
        argv = argv or sys.argv[1:]
        try:
            cmd = typer.main.get_command(self.app)
            cmd.main(args=argv, prog_name="obk", standalone_mode=False)
        except DivisionByZeroError as exc:
            logging.getLogger(__name__).exception("Division error")
            typer.echo(f"[ERROR] {exc}", err=True)
            sys.exit(2)


def main(argv: list[str] | None = None) -> None:
    """Entry point for ``python -m obk``."""
    ObkCLI().run(argv)
