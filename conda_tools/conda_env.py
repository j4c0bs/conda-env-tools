# -*- coding: utf-8 -*-

import logging
import os

from pathlib import Path


logger = logging.getLogger(__name__)


def confirm_active():
    if "CONDA_PREFIX" not in os.environ:
        raise ImportError(
            "$CONDA_PREFIX not found. Activate a conda env before running..."
        )
    return None


def is_base_env(prefix):
    """Detect if active conda env is `base`.

    Args:
        prefix (pathlib.Path): conda env prefix path

    Returns:
        type: bool
    """

    return "envs" not in prefix.parts and "conda" in prefix.stem


def is_conda_env(conda_env_name):
    conda_prefix = get_prefix(allow_base=True)

    if is_base_env(conda_prefix):
        conda_prefix = conda_prefix / "envs"
    else:
        conda_prefix = conda_prefix.parent

    prefix = conda_prefix / conda_env_name
    return prefix


def get_prefix(allow_base=False):
    """Get $CONDA_PREFIX as pathlib.Path object."""

    confirm_active()
    prefix = Path(os.environ.get("CONDA_PREFIX"))

    if not allow_base and is_base_env(prefix):
        raise ImportError(
            "Base conda env detected, activate an environment before running this command..."
        )

    return prefix
