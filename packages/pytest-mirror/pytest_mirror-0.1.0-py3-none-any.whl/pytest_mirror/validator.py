"""Validator implementation for pytest-mirror."""

from pathlib import Path

import pluggy

from .constants import PACKAGE_NAME
from .core import find_missing_tests

hookimpl = pluggy.HookimplMarker(PACKAGE_NAME)


class MirrorValidator:
    """Plugin implementation that enforces mirrored test structure."""

    @hookimpl
    def validate_test_structure(self, package_dir: Path, tests_dir: Path) -> list[Path]:
        """Return missing test file paths."""
        return find_missing_tests(package_dir, tests_dir)
