import signal
import sys
import threading
from importlib import metadata
from pathlib import Path
from types import FrameType
from typing import Annotated

import typer

from .concurrent_monitor import monitor_serial
from .concurrent_monitor import offline_mode
from .helper_serial import serial_port_list
from .logger import increase_verbose_level
from .logger import log

cli = typer.Typer(help="A serial monitor and analysis tool")


def exit_gracefully(_signum: int, _frame: FrameType | None) -> None:
    log.warning("Exiting!")
    sys.exit(0)


verbose_opt_t = typer.Option(
    False,  # noqa: FBT003
    "--verbose",
    "-v",
    help="Sets logging-level to debug",
)


@cli.callback()
def cli_callback(*, verbose: bool = verbose_opt_t) -> None:
    """Enable verbosity and add exit-handlers.

    this gets executed prior to the other sub-commands
    """
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, exit_gracefully)
    increase_verbose_level(3 if verbose else 2)


@cli.command()
def version() -> None:
    """Print version-infos (combinable with -v)."""
    log.info("testsoftware-monitor v%s", metadata.version("testsoftware_monitor"))
    log.debug("Python v%s", sys.version)

    for package in ["cbor2", "typer", "click"]:
        log.debug("%s v%s", package, metadata.version(package))


@cli.command()
def load(path: Path) -> None:
    """Process stored data."""
    offline_mode(path)


@cli.command("list")
def list_ports() -> None:
    """List available serial-ports."""
    serial_ports = serial_port_list()
    log.info("Available Ports: %s", serial_ports)


@cli.command()
def serial(
    serial_ports: Annotated[
        list[str] | None, typer.Option(help="will capture every port when omitted")
    ] = None,
) -> None:
    """Process live data coming from serial port."""
    if serial_ports is None:
        serial_ports = serial_port_list()
    if isinstance(serial_ports, str):
        serial_ports = [serial_ports]

    log.info("Receiving Ports: %s", serial_ports)
    log.info("Note: current implementation only allows 1 Monitor -> will select first in list")
    log.info("Note: press ctrl+c to end service")

    monitor_serial(serial_ports[0])

    uart_threads: list[threading.Thread] = []
    for port in serial_ports:
        uart_thread = threading.Thread(
            target=monitor_serial,
            args=(port),
            daemon=True,
        )
        uart_thread.start()
        uart_threads.append(uart_thread)

    for uart_thread in uart_threads:
        uart_thread.join()


if __name__ == "__main__":
    cli()
