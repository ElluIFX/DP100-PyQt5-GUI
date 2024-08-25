import logging
import sys
import types
from datetime import datetime
from logging import LogRecord
from types import TracebackType
from typing import Any, Callable, Dict, Iterable, List, Optional, Type, Union

from loguru import logger
from loguru._logger import Core
from rich.console import Console, ConsoleRenderable
from rich.highlighter import Highlighter
from rich.logging import RichHandler
from rich.text import Text
from rich.theme import Theme

for lv in Core().levels.values():
    logging.addLevelName(lv.no, lv.name)


class LoggingToLoguruHandler(logging.Handler):
    """Redirecting logging's messages to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message.
        frame, depth = logging.currentframe(), 2
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        message = record.getMessage()

        # # remove timestamp like [19/Sep/2023 14:08:16]
        # message = re.sub(r"\[\d+/\w+/\d{4} \d{2}:\d{2}:\d{2}\] ", "", message)
        # # remove terminal color code
        # message = re.sub(r"\x1b\[\d+m", "", message)
        # message = re.sub(r"\x1b\[\d+;\d+m", "", message)

        logger.opt(depth=depth, exception=record.exc_info).log(level, message)


def highlight(style: str) -> Dict[str, Callable[[Text], Text]]:
    """Add `style` to RichHandler's log text.

    Example:
    ```py
    logger.warning("Sth is happening!", **highlight("red bold"))
    ```
    """

    def highlighter(text: Text) -> Text:
        return Text(text.plain, style=style)

    return {"highlighter": highlighter}


class LoguruRichHandler(RichHandler):
    """
    Interpolate RichHandler in a better way

    Example:

    ```py
    logger.warning("Sth is happening!", style="red bold")
    logger.warning("Sth is happening!", **highlight("red bold"))
    logger.warning("Sth is happening!", alt="[red bold]Sth is happening![/red bold]")
    logger.warning("Sth is happening!", text=Text.from_markup("[red bold]Sth is happening![/red bold]"))
    ```
    """

    def __init__(self, **kwargs: Any):
        self.__time_single_line = kwargs.pop("time_single_line", False) and kwargs.get(
            "show_time", True
        )
        if self.__time_single_line:
            kwargs["show_time"] = False
        super().__init__(**kwargs)

    def render_message(self, record: LogRecord, message: str) -> "ConsoleRenderable":
        # alternative time log
        if self.__time_single_line:
            time_format = None if self.formatter is None else self.formatter.datefmt
            time_format = time_format or self._log_render.time_format
            log_time = datetime.fromtimestamp(record.created)
            if callable(time_format):
                log_time_display = time_format(log_time)
            else:
                log_time_display = Text(log_time.strftime(time_format))
            if not (
                log_time_display == self._log_render._last_time
                and self._log_render.omit_repeated_times
            ):
                self.console.print(log_time_display, style="log.time")
                self._log_render._last_time = log_time_display

        # add extra attrs to record
        extra: dict = getattr(record, "extra", {})
        if "rich" in extra:
            return extra["rich"]
        if "style" in extra:
            record.__dict__.update(highlight(extra["style"]))
        elif "highlighter" in extra:
            setattr(record, "highlighter", extra["highlighter"])
        if "alt" in extra:
            message = extra["alt"]
            setattr(record, "markup", True)
        if "markup" in extra:
            setattr(record, "markup", extra["markup"])
        if "text" in extra:
            setattr(record, "highlighter", lambda _: extra["text"])
        return super().render_message(record, message)


ExceptionHook = Callable[
    [Type[BaseException], BaseException, Optional[TracebackType]], Any
]


def loguru_exc_hook(
    typ: Type[BaseException], val: BaseException, tb: Optional[TracebackType]
):
    
    logger.opt(exception=(typ, val, tb)).critical("Unhandled exception occurred")


DefaultTheme = Theme(
    {
        "log.time": "pale_green3",
        "log.path": "dim cyan",
        "logging.level.info": "steel_blue1",
        "logging.level.warning": "bright_yellow",
        "logging.level.success": "green_yellow",
        "logging.level.trace": "bright_black",
    }
)


def install(
    level: Union[int, str] = "TRACE",
    console: Optional[Console] = None,
    *,
    theme: Optional[Theme] = DefaultTheme,
    exc_hook: Optional[ExceptionHook] = loguru_exc_hook,
    redirect_logging: bool = True,
    show_time: bool = True,
    omit_repeated_times: bool = True,
    time_single_line: bool = False,
    time_format: Union[str, Callable[[datetime], Text]] = "[%d/%X]",
    show_path: bool = True,
    enable_link_path: bool = True,
    keywords: Optional[List[str]] = None,
    highlighter: Optional[Highlighter] = None,
    markup: bool = False,
    rich_traceback: bool = True,
    tracebacks_extra_lines: int = 3,
    tracebacks_theme: Optional[str] = None,
    tracebacks_show_locals: bool = True,
    tracebacks_suppress: Iterable[Union[str, types.ModuleType]] = (),
    **kwargs: Any,
) -> Console:
    """Install LoguruRichHandler to loguru, logging and sys.excepthook.

    Args:
        level (Union[int, str]): Log level. Defaults to "DEBUG".
        console (:class:`~rich.console.Console`): Optional console instance to write logs.
            Default will use a global console instance writing to stdout.
        theme (Theme): Optional theme to push onto the console.
        exc_hook (ExceptionHook): Optional exception hook to use for unhandled exceptions.
        redirect_logging (bool): Redirect logging to Loguru. Defaults to True.
            Defaults to loguru_exc_hook, setting to None will disable exception hook.
        show_time (bool, optional): Show a column for the time. Defaults to True.
        omit_repeated_times (bool, optional): Omit repetition of the same time. Defaults to True.
        time_single_line (bool): Display time on a single line. Defaults to False.
        time_format (Union[str, Callable[[datetime], Text]]): Format string or callable to format log time.
        show_path (bool): Show the path to the original log call. Defaults to True.
        enable_link_path (bool): Enable terminal link of path column to file. Defaults to True.
        keywords (List[str]): List of words to highlight instead of ``RichHandler.KEYWORDS``.
        highlighter (Highlighter): Highlighter to style log messages, or None to use ReprHighlighter. Defaults to None.
        markup (bool): Enable console markup in log messages. Defaults to False.
        rich_tracebacks (bool): Enable rich tracebacks with syntax highlighting and formatting. Defaults to False.
        tracebacks_extra_lines (int): Additional lines of code to render tracebacks, or None for full width. Defaults to None.
        tracebacks_theme (str): Override pygments theme used in traceback.
        tracebacks_show_locals (bool): Enable display of locals in tracebacks. Defaults to False.
        tracebacks_suppress (Sequence[Union[str, ModuleType]]): Optional sequence of modules or paths to exclude from traceback.

        More kwargs are passed to RichHandler.

    Returns:
        Console: The console instance used for logging.
    """
    if redirect_logging:
        logging.basicConfig(
            handlers=[LoggingToLoguruHandler(0)],
            level=0,
            force=True,
            format="%(message)s",
            datefmt=None,
        )
    console_instance = console or Console()
    if theme is not None:
        console_instance.push_theme(theme=theme)
    logger.configure(
        handlers=[
            {
                "sink": LoguruRichHandler(
                    console=console_instance,
                    show_time=show_time,
                    omit_repeated_times=omit_repeated_times,
                    time_single_line=time_single_line,
                    log_time_format=time_format,
                    keywords=keywords,
                    highlighter=highlighter,
                    show_path=show_path,
                    enable_link_path=enable_link_path,
                    markup=markup,
                    rich_tracebacks=rich_traceback,
                    tracebacks_show_locals=tracebacks_show_locals,
                    tracebacks_suppress=tracebacks_suppress,
                    tracebacks_extra_lines=tracebacks_extra_lines,
                    tracebacks_theme=tracebacks_theme,
                    **kwargs,
                ),
                "format": (lambda _: "{message}") if rich_traceback else "{message}",
                "level": level.upper() if isinstance(level, str) else level,
            }
        ]
    )
    if exc_hook is not None:
        sys.excepthook = exc_hook
    return console_instance


if __name__ == "__main__":
    import time

    console = install(level="TRACE")
    log = logging.getLogger("test")
    log.setLevel(logging.DEBUG)
    t0 = time.perf_counter()
    logger.info("Hello, World!")
    logger.warning("This is a warning!")
    logger.error("This is an error!")
    logger.critical("This is critical!")
    logger.debug("This is debug!")
    logger.trace("This is trace!")
    logger.success("This is success!")
    t1 = time.perf_counter()
    print(f"Loguru cost: {(t1-t0)/7:.6f} seconds")

    t0 = time.perf_counter()
    log.debug("This is a debug message from logging")
    log.info("This is an info message from logging")
    log.warning("This is a warning message from logging")
    log.error("This is an error message from logging")
    log.critical("This is a critical message from logging")
    t1 = time.perf_counter()
    print(f"Logging cost: {(t1-t0)/5:.6f} seconds")

    from rich.color import ANSI_COLOR_NAMES

    logger.debug(
        f"{len(ANSI_COLOR_NAMES)} Color test: "
        + " ".join(f"[{color}]{color}[/{color}]" for color in ANSI_COLOR_NAMES),
        markup=True,
    )
