# -*- coding: utf-8 -*-

import logging
import os.path
from pathlib import Path
import platform

from . import conda_env

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------


def unset_vars(env_vars_path):
    clean = []

    for line in env_vars_path.read_text().split("\n"):
        if line.startswith("export"):
            var = line.split()[1].split("=")[0]
            clean.append(f"unset {var}")
        else:
            clean.append(line)
    return "\n".join(clean)


# --------------------------------------------------------------------------------------


def env_var_subdirs():
    """Construct conda env var file directory paths."""

    parents = ("etc", "conda")
    subdirs = []
    for dir_prefix in ("", "de"):
        subdir = os.path.join(*parents, f"{dir_prefix}activate.d")
        subdirs.append(subdir)
    return subdirs


def get_env_path(prefix, activate=True):

    ext = "sh" if platform.system().lower() != "windows" else "bat"
    dir_prefix = "" if activate else "de"
    path = prefix / "etc" / "conda" / f"{dir_prefix}activate.d" / f"env_vars.{ext}"
    return path


def load_env_paths(path_prefix):
    """Construct paths for de/activate shell files.

    Args:
        path_prefix (pathlib.Path):
            - Path prefix for env files

    Returns:
        type: pathlib.Path, pathlib.Path
    """

    subdir_activate, subdir_deactivate = env_var_subdirs()
    env_activate = path_prefix / subdir_activate / "env_vars.sh"
    env_deactivate = path_prefix / subdir_deactivate / "env_vars.sh"
    return env_activate, env_deactivate


def _copy_env_file(env_path, conda_prefix, output_dir=None):
    """Copy de/activate env var file to output_dir."""

    if not output_dir:
        output_dir = Path.cwd()

    activate = "activate.d" in env_path.parts
    out_path = output_dir / get_env_path(Path(conda_prefix.stem), activate=activate)

    if out_path.exists():
        raise FileExistsError(f"Env file exists: {out_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(env_path.read_text())
    logger.info(f"Copied {env_path} to {out_path}")


def export_env_files(conda_prefix=None, output_dir=None):
    """Export a copy of conda env var files to local dir.

    Args:
        conda_prefix (pathlib.Path):
            - Path prefix for env files
        output_dir (pathlib.Path):
            - location to store files
            - defaults to cwd
    """

    if not conda_prefix:
        conda_prefix = conda_env.get_prefix()

    path_activate = get_env_path(conda_prefix, activate=True)
    path_deactivate = get_env_path(conda_prefix, activate=False)

    for path in (path_activate, path_deactivate):
        if path.exists():
            _copy_env_file(path, conda_prefix, output_dir=output_dir)
        else:
            logger.warning(f"No env var file exists for {path}...")


def copy_env_files(src_prefix, dest_prefix):
    """Export a copy of conda env var files to local dir.

    Args:
        src_prefix (pathlib.Path):
            - Path prefix for env files

        dest_prefix (pathlib.Path):
            - Destination path prefix
    """

    src_paths = load_env_paths(src_prefix)
    dest_paths = load_env_paths(dest_prefix)

    for src, dest in zip(src_paths, dest_paths):
        if src.exists() and not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(src.read_text())
            logger.info(f"Copied {src} to {dest}")
        else:
            if not src.exists():
                msg = f"Source env var does not exist: {src}"
                raise FileNotFoundError(msg)
            if dest.exists():
                msg = f"Destination env var exists: {dest}"
                raise FileExistsError(msg)


if __name__ == "__main__":
    export_env_files()
