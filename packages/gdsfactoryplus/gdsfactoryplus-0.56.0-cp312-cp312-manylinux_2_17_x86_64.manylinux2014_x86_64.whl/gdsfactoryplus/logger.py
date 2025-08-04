"""GDSFactory+ Logger."""

import os
import sys
from functools import cache
from pathlib import Path
from typing import Any, TypeAlias

__all__ = ["Logger", "fix_log_line_numbers", "get_logger"]

Logger: TypeAlias = Any  # TODO: fix


@cache
def get_logger() -> Logger:
    """Get the GDSFactory+ logger."""
    return _setup_logger()


def fix_log_line_numbers(content: str) -> str:
    """Patches a different format for file + line nr combination into logs."""
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if '", line ' in line:
            first, rest = line.split('", line ')
            nbr, rest = rest.split(",")
            lines[i] = f'{first}:{nbr}",{rest}'
    return "\n".join(lines)


def _setup_logger() -> Logger:
    """Logger setup."""
    from logging.handlers import RotatingFileHandler

    from loguru import logger

    from .project import maybe_find_docode_project_dir
    from .settings import get_settings

    settings = get_settings()

    project_dir = Path(maybe_find_docode_project_dir() or Path.cwd())
    ws_port_path = Path(project_dir) / "build" / "log" / "_server.log"
    ws_port_path.parent.mkdir(parents=True, exist_ok=True)
    ws_port_path.touch(exist_ok=True)
    logger.remove()
    _format = "{time:HH:mm:ss} | {level: <8} | {message}"
    os.makedirs(os.path.dirname(os.path.abspath(ws_port_path)), exist_ok=True)
    logger.add(sys.stdout, level=settings.log.level, colorize=True, format=_format)
    logger.add(
        RotatingFileHandler(ws_port_path, maxBytes=20 * 1024 * 1024, backupCount=14),
        level=settings.log.debug_level,
        format=_format,
    )
    return logger
