# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
import sys

from . import conda_env, export_env_vars, versionator
from . import __version__ as version


def valid_env_name(name):
    """Confirm valid conda env name.

    Arg:
        name (str): name of env

    Returns:
        type: pathlib.Path
    """

    path = conda_env.is_conda_env(name)
    if not path.exists():
        msg = f"Conda env {name} does not exist..."
        raise argparse.ArgumentTypeError(msg)
    return path


def valid_path(filepath):
    """Confirm valid filepath.

    Arg:
        filepath (str): infile

    Returns:
        type: pathlib.Path
    """

    path = Path(filepath)
    if not path.exists():
        msg = f"File {path} does not exist..."
        raise argparse.ArgumentTypeError(msg)
    return path


def valid_directory(filepath):
    """Confirm valid directory path.

    Arg:
        filepath (str): input directory

    Returns:
        type: pathlib.Path
    """

    path = Path(filepath)

    if path.is_file():
        msg = f"Input directory is a file: {path}"
        raise argparse.ArgumentTypeError(msg)

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def add_env_src_arg(group):
    """Add src_env argument to subparser group."""

    group.add_argument(
        "-s",
        "--src_env",
        type=valid_env_name,
        default=conda_env.get_prefix(),
        help="Source conda env - defaults to current env",
    )


def parse_arguments():
    """Parse CLI args."""

    parser = argparse.ArgumentParser(description="conda env tools",)

    parser.add_argument("-v", "--version", action="version", version=version)

    subparsers = parser.add_subparsers(dest="command", title="commands")

    # Copy env files between conda environments
    env_cp_parser = subparsers.add_parser(
        "copy_vars", aliases=[], help="Copy env vars file to another conda env"
    )

    env_cp_group = env_cp_parser.add_argument_group(title="copy options")
    add_env_src_arg(env_cp_group)

    env_cp_group.add_argument(
        "-d", "--dest_env", type=valid_env_name, help="Destination conda env"
    )

    env_cp_group.add_argument(
        "-l",
        "--local_dir",
        type=valid_path,
        help="Local env var file dir to export - replaces src_env",
    )

    # Export env files to local directory
    env_export_parser = subparsers.add_parser(
        "export_vars", aliases=[], help="Export env vars file to local dir"
    )

    env_export_group = env_export_parser.add_argument_group(title="export options")
    add_env_src_arg(env_export_group)

    env_export_group.add_argument(
        "-o",
        "--output_dir",
        type=valid_directory,
        default=Path.cwd(),
        help="Directory to copy files into - defaults to cwd",
    )

    # Update pkg versions in env yml file
    pkg_ver_parser = subparsers.add_parser(
        "ver", aliases=[], help="(De)Version dependencies in conda env yml file"
    )

    pkg_ver_group = pkg_ver_parser.add_argument_group(title="export options")

    pkg_ver_group.add_argument("-x", action="store_true", help="Strip package versions")

    pkg_ver_group.add_argument(
        dest="infile",
        type=argparse.FileType("r"),
        nargs="?",
        default=sys.stdin,
        help="Conda env file or output from `conda env export`",
    )

    args = parser.parse_args()
    return args


def run_cli():
    args = parse_arguments()

    if args.command == "copy_vars":
        export_env_vars.copy_env_files(args.src_env, args.dest_env)
    elif args.command == "export_vars":
        export_env_vars.export_env_files(
            conda_prefix=args.src_env, output_dir=args.output_dir
        )
    elif args.command == "ver":
        versionator.write_pkg_versions(args.infile, deversion=args.x)


if __name__ == "__main__":
    run_cli()
