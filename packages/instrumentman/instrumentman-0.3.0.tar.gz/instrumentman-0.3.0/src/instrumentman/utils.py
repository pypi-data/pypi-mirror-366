from logging import DEBUG, ERROR, INFO, WARNING, Logger
import os
from typing import Any, Callable, cast, TypeVar

from click_extra import (
    Color,
    echo,
    style,
    option,
    option_group,
    argument,
    Choice,
    IntRange
)
from cloup.constraints import mutually_exclusive


F = TypeVar('F', bound=Callable[..., Any])


EXIT_CODE_DESCRIPTIONS: dict[int, str] = {
    1: "Unknown",
    2: "Keyboard interrupt",
    3: "Missing dependencies",
    4: "Malformed data",
    1100: "Error in target point CSV",
    1101: "Duplicate targets between CSV and existing JSON",
    1102: "Error while opening point CSV",
    1103: "Target CSV file does not exist",
    1200: "Unknown measurement order"
}


def com_port_argument() -> Callable[[F], F]:
    return argument(
        "port",
        help=(
            "serial port that the instrument is connected to (must be a valid "
            "identifier like COM1 or /dev/usbtty0)"
        ),
        type=str
    )


def com_timeout_option(
    default: int = 15
) -> Callable[[F], F]:
    return option(
        "-t",
        "--timeout",
        help="serial timeout",
        type=IntRange(min=0),
        default=default
    )


def com_baud_option(
    default: int = 9600
) -> Callable[[F], F]:
    return option(
        "-b",
        "--baud",
        help="serial speed",
        type=Choice(
            [
                "1200",
                "2400",
                "4800",
                "9600",
                "19200",
                "38400",
                "56000",
                "57600",
                "115200",
                "230400",
                "921600"
            ]
        ),
        callback=lambda ctx, param, value: int(value),
        default=str(default)
    )


def com_option_group() -> Callable[[F], F]:
    return option_group(
        "Connection options",
        "Options related to the serial connection",
        com_baud_option(),
        com_timeout_option(),
        option(
            "-r",
            "--retry",
            help="number of connection retry attempts",
            type=IntRange(min=0, max=10),
            default=1
        ),
        option(
            "--sync-after-timeout",
            help="attempt to synchronize message que after a timeout",
            is_flag=True
        )
    )


def logging_option_group() -> Callable[[F], F]:
    return option_group(
        "Logging options",
        "Options related to the logging functionalities.",
        option(
            "--debug",
            is_flag=True
        ),
        option(
            "--info",
            is_flag=True
        ),
        option(
            "--warning",
            is_flag=True
        ),
        option(
            "--error",
            is_flag=True
        ),
        constraint=mutually_exclusive
    )


def echo_color(
    message: Any,
    color: str,
    newline: bool = True,
    error: bool = False
) -> None:
    echo(
        style(
            message,
            color
        ),
        nl=newline,
        err=error
    )


def echo_yellow(
    message: Any,
    newline: bool = True,
    error: bool = False
) -> None:
    echo_color(message, Color.yellow, newline, error)


def echo_green(
    message: Any,
    newline: bool = True,
    error: bool = False
) -> None:
    echo_color(message, Color.green, newline, error)


def echo_red(
    message: Any,
    newline: bool = True,
    error: bool = False
) -> None:
    echo_color(message, Color.red, newline, error)


def make_directory(filepath: str) -> None:
    dirname = os.path.dirname(filepath)
    if dirname == "":
        return

    os.makedirs(dirname, exist_ok=True)


def make_logger(
    name: str,
    debug: bool = False,
    info: bool = False,
    warning: bool = False,
    error: bool = False
) -> Logger:
    from geocompy.communication import get_logger

    if debug:
        loglevel = DEBUG
    elif info:
        loglevel = INFO
    elif warning:
        loglevel = WARNING
    elif error:
        loglevel = ERROR
    else:
        return get_logger(name)

    return get_logger(name, "stdout", loglevel)


def run_cli_app(
    name: str,
    runner: Callable[..., Any],
    *args: Any
) -> None:
    logger = make_logger("APP", info=True)
    try:
        logger.info(f"Starting '{name}' application")
        runner(args)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt...")
        exit(2)
    except SystemExit as ex:
        if ex.code == 0:
            logger.info(f"Application '{name}' exited without error")
            raise ex

        logger.error(
            f"Application exited with {ex.code} "
            f"({EXIT_CODE_DESCRIPTIONS.get(cast(int, ex.code), 'Unknown')})"
        )
        raise ex
    except Exception:
        logger.exception(
            f"Application '{name}' exited due to an unhandled exception"
        )
        exit(1)

    logger.info(f"Application '{name}' finished without error")
    exit(0)
