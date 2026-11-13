"""Find the node classes in a folder of Python files."""

from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType

from node_editor.node import Node

logger = logging.getLogger(__name__)


def load_node_classes(folder: Path) -> dict[str, type[Node]]:
    """Import each Python file in `folder`, and return its Node subclasses by class name.

    The loader skips files with a name that starts with "_" (for example __init__.py).
    If a file cannot be imported, the loader skips it and writes the error to the log.
    """
    node_classes: dict[str, type[Node]] = {}
    for path in sorted(folder.glob("*.py")):
        if path.name.startswith("_"):
            continue
        try:
            module = _import_file(path)
        except Exception:
            logger.exception("Cannot import %s", path)
            continue

        for value in vars(module).values():
            # Use only the classes that the file defines, not the classes that it imports.
            if isinstance(value, type) and issubclass(value, Node) and value.__module__ == module.__name__:
                node_classes[value.__name__] = value
    return node_classes


def _import_file(path: Path) -> ModuleType:
    """Import one Python file as a module."""
    module_name = f"{path.parent.name}.{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
